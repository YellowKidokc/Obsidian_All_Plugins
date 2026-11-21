export type ProviderId = 'openai' | 'deepseek' | 'anthropic' | 'ollama' | 'custom' | 'openrouter';

export const PROVIDER_IDS: ProviderId[] = ['openai', 'deepseek', 'anthropic', 'ollama', 'custom'];

/** Per-provider credentials. Kept separately so switching provider keeps both keys. */
export interface ProviderConfig {
  apiKey: string;
  endpoint: string;
  model: string;
}

/** How a provider's HTTP request is shaped. */
export type WireFormat = 'openai' | 'anthropic' | 'ollama';

export interface ProviderInfo {
  name: string;
  wireFormat: WireFormat;
  defaultEndpoint: string;
  defaultModel: string;
  requiresKey: boolean;
  /** Where to get a key, shown in settings. */
  keyUrl: string;
  suggestedModels: string[];
}

export const PROVIDERS: Record<ProviderId, ProviderInfo> = {
  openai: {
    name: 'OpenAI',
    wireFormat: 'openai',
    defaultEndpoint: 'https://api.openai.com/v1/chat/completions',
    defaultModel: 'gpt-4o-mini',
    requiresKey: true,
    keyUrl: 'https://platform.openai.com/api-keys',
    suggestedModels: ['gpt-4o-mini', 'gpt-4o', 'gpt-4.1-mini', 'gpt-4.1']
  },
  deepseek: {
    name: 'DeepSeek',
    wireFormat: 'openai',
    defaultEndpoint: 'https://api.deepseek.com/chat/completions',
    defaultModel: 'deepseek-chat',
    requiresKey: true,
    keyUrl: 'https://platform.deepseek.com/api_keys',
    suggestedModels: ['deepseek-chat', 'deepseek-reasoner']
  },
  anthropic: {
    name: 'Anthropic',
    wireFormat: 'anthropic',
    defaultEndpoint: 'https://api.anthropic.com/v1/messages',
    defaultModel: 'claude-3-5-haiku-latest',
    requiresKey: true,
    keyUrl: 'https://console.anthropic.com/settings/keys',
    suggestedModels: ['claude-3-5-haiku-latest', 'claude-sonnet-4-5', 'claude-opus-4-1']
  },
  ollama: {
    name: 'Ollama (local)',
    wireFormat: 'ollama',
    defaultEndpoint: 'http://localhost:11434/api/generate',
    defaultModel: 'llama3.1',
    requiresKey: false,
    keyUrl: 'https://ollama.com',
    suggestedModels: ['llama3.1', 'mistral', 'qwen2.5']
  },
  openrouter: {
    name: 'OpenRouter',
    wireFormat: 'openai',
    defaultEndpoint: 'https://openrouter.ai/api/v1/chat/completions',
    defaultModel: '',
    requiresKey: true,
    keyUrl: 'https://openrouter.ai/settings/keys',
    suggestedModels: []
  },
  custom: {
    name: 'Custom endpoint',
    wireFormat: 'openai',
    defaultEndpoint: '',
    defaultModel: '',
    requiresKey: false,
    keyUrl: '',
    suggestedModels: []
  }
};

/** Resolved connection details for the provider that is currently selected. */
export function activeProvider(settings: { provider: ProviderId; providers?: Partial<Record<ProviderId, ProviderConfig>> }): {
  id: ProviderId;
  config: ProviderConfig;
  endpoint: string;
  model: string;
} {
  const id = settings.provider;
  const info = PROVIDERS[id] || PROVIDERS.openai;
  const config = settings.providers?.[id] || { apiKey: '', endpoint: '', model: '' };

  return {
    id,
    config,
    endpoint: config.endpoint || info.defaultEndpoint,
    model: config.model || info.defaultModel
  };
}
