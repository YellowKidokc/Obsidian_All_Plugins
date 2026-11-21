import catalog from '../../../docs/series-automation-reference/config/task_registry.reference.json';
import prompts from '../../../docs/series-automation-reference/docs/discovery/PROMPT_CANDIDATES.md';
import rigor from '../../../docs/series-automation-reference/config/rigor_areas.json';
import orbits from '../../../docs/series-automation-reference/config/orbits28.reference.json';
import outputs from '../../../docs/series-automation-reference/docs/discovery/DESIRED_OUTPUTS.json';
export { default as roles } from '../../../docs/series-automation-reference/config/roles.json';
export { default as pending } from '../../../docs/series-automation-reference/docs/discovery/PROPOSED_ADDITIONAL_OUTPUTS.json';
export { rigor, outputs, orbits };

export const modes = ['preview', 'annotation', 'record', 'generated-note', 'export', 'callout'] as const;
export type Mode = typeof modes[number];

export const tasks = catalog.task_families.flatMap(family => {
  const section = family.prompt_source && prompts.split(family.prompt_source.heading + '\n')[1]?.split('\n###')[0];
  const candidates = section ? Array.from(section.matchAll(/^> (.+)$/gm), match => match[1]) : [];
  const outputIds = family.desired_outputs ?? [];
  const relatedOutputs = outputs.outputs.filter(output => outputIds.includes(output.output_id));
  const areas = relatedOutputs.flatMap(output => output.rigor.match(/\b\d{2}\b/g) ?? []);
  return family.task_classes.map((taskClass, index) => {
    const prompt = family.prompt ?? candidates[index] ?? candidates[0];
    if (!prompt) throw new Error('Missing prompt for ' + family.task_family);
    return {
      id: family.task_family + '/' + taskClass,
      title: family.title?.split(' — ')[0] ?? family.task_family,
      taskClass,
      roles: family.roles,
      rigor: [...new Set(areas)],
      outputIds,
      promptVersion: catalog.schema,
      responseSchema: 'semantic-series.findings/1',
      prompt: 'Perform only the ' + taskClass + ' task. ' + prompt +
        ' Scope your response to this task class. Report missing context and cannot_assess where required.',
      requiredContext: family.task_family === 'canon_assess'
        ? ['Exact edition, applicable rules and rulings, validated findings, open blockers and receipts']
        : family.task_family === 'orbits28_extract' ? ['Exact edition and the ORBITS contract']
        : relatedOutputs.map(output => output.inputs),
      defaultMode: 'preview' as const,
      review: 'Human exact-version review',
      allowedModes: modes
    };
  });
});

export const orbitsFields = Object.values(orbits.groups).flat();
