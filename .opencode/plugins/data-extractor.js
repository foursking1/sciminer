/**
 * Data Extractor Plugin for OpenCode
 *
 * Auto-registers data-extractor skills directory.
 */

import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const DataExtractorPlugin = async ({ client, directory }) => {
  // Resolve skills directory relative to plugin location
  const skillsDir = path.resolve(__dirname, '../../skills');

  return {
    // Inject skills path into config so OpenCode discovers data-extractor skills
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(skillsDir)) {
        config.skills.paths.push(skillsDir);
      }
    },

    // Optionally inject system prompt context
    'experimental.chat.system.transform': async (_input, output) => {
      output.system.push(`
<DATA-EXTRACTOR-AVAILABLE>
The data-extractor skill is available for extracting structured data from scientific documents.
Use OpenCode's native \`skill\` tool to load and use data extraction skills.
Available schemas: fossil, shale_gas
</DATA-EXTRACTOR-AVAILABLE>`);
    }
  };
};
