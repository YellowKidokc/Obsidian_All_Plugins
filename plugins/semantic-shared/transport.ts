import { activeProvider, PROVIDERS } from './providers';

interface ProviderRequest {
  url: string;
  method: string;
  headers: Record<string, string>;
  body: string;
  throw: boolean;
}

export class ProviderTransport {
  constructor(
    private connection: ReturnType<typeof activeProvider>,
    private request: (params: ProviderRequest) => Promise<{status: number; text: string; json: any}>
  ) {}

  /**
   * Send a prompt to the active provider and return the raw text reply.
   * Public so other features can reuse the same transport and credentials.
   */
  async complete(prompt: string, maxTokens = 4096): Promise<string> {
    const { id, config, endpoint, model } = this.connection;
    const info = PROVIDERS[id] || PROVIDERS.openai;

    if (info.requiresKey && !config.apiKey) {
      throw new Error(`No API key set for ${info.name}. Add one in the plugin settings.`);
    }

    if (!endpoint) {
      throw new Error(`No endpoint set for ${info.name}. Add one in the plugin settings.`);
    }

    switch (info.wireFormat) {
      case 'anthropic':
        return this.callAnthropic(endpoint, config.apiKey, model, prompt, maxTokens);
      case 'ollama':
        return this.callOllama(endpoint, model, prompt);
      case 'openai':
      default:
        return this.callOpenAICompatible(endpoint, config.apiKey, model, prompt, maxTokens, info.name);
    }
  }

  /** OpenAI, DeepSeek, and any other chat-completions-compatible endpoint. */
  private async callOpenAICompatible(
    endpoint: string,
    apiKey: string,
    model: string,
    prompt: string,
    maxTokens: number,
    providerName: string
  ): Promise<string> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (apiKey) {
      headers['Authorization'] = `Bearer ${apiKey}`;
    }

    const requestParams: ProviderRequest = {
      url: endpoint,
      method: 'POST',
      headers,
      body: JSON.stringify({
        model,
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.3,
        max_tokens: maxTokens
      }),
      throw: false
    };

    const response = await this.request(requestParams);

    if (response.status !== 200) {
      throw new Error(`${providerName} error ${response.status}: ${this.errorDetail(response.text)}`);
    }

    const data = response.json;
    const text = data?.choices?.[0]?.message?.content;

    if (typeof text !== 'string') {
      throw new Error(`${providerName} returned an unexpected response shape.`);
    }

    return text;
  }

  private async callAnthropic(
    endpoint: string,
    apiKey: string,
    model: string,
    prompt: string,
    maxTokens: number
  ): Promise<string> {
    const requestParams: ProviderRequest = {
      url: endpoint,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model,
        max_tokens: maxTokens,
        messages: [{ role: 'user', content: prompt }]
      }),
      throw: false
    };

    const response = await this.request(requestParams);

    if (response.status !== 200) {
      throw new Error(`Anthropic error ${response.status}: ${this.errorDetail(response.text)}`);
    }

    const data = response.json;
    const text = data?.content?.[0]?.text;

    if (typeof text !== 'string') {
      throw new Error('Anthropic returned an unexpected response shape.');
    }

    return text;
  }

  private async callOllama(endpoint: string, model: string, prompt: string): Promise<string> {
    const requestParams: ProviderRequest = {
      url: endpoint,
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, prompt, stream: false }),
      throw: false
    };

    const response = await this.request(requestParams);

    if (response.status !== 200) {
      throw new Error(`Ollama error ${response.status}: ${this.errorDetail(response.text)}`);
    }

    const data = response.json;

    if (typeof data?.response !== 'string') {
      throw new Error('Ollama returned an unexpected response shape.');
    }

    return data.response;
  }

  /** Pull a readable message out of an error body without dumping the whole payload. */
  private errorDetail(body: string): string {
    if (!body) {
      return 'no response body';
    }

    try {
      const parsed = JSON.parse(body);
      const message = parsed?.error?.message || parsed?.error || parsed?.message;
      if (typeof message === 'string') {
        return message;
      }
    } catch {
      // Not JSON — fall through to the truncated raw body.
    }

    return body.length > 300 ? `${body.slice(0, 300)}…` : body;
  }

}
