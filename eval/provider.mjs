import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
const execFileAsync = promisify(execFile);
const here = path.dirname(fileURLToPath(import.meta.url));
const cases = JSON.parse(fs.readFileSync(path.join(here, 'cases.json'), 'utf8'));
export default class CronMasterProvider {
  constructor(options = {}) { this.config = options.config || {}; }
  id() { return this.config.negativeControl ? 'cron-master-negative-control' : 'cron-master-component-tests'; }
  async callApi(_prompt, context) {
    const name = context?.vars?.case_id;
    if (typeof name !== 'string' || !Object.hasOwn(cases, name)) return { error: 'Case is not in the fixed allowlist' };
    const python = process.env.CRON_MASTER_PYTHON || (process.platform === 'win32' ? 'python.exe' : 'python3');
    const args = [path.join(here, 'run_case.py'), name];
    if (this.config.negativeControl === true) args.push('--negative-control');
    try {
      const { stdout } = await execFileAsync(python, args, { cwd: path.dirname(here), timeout: 15000, maxBuffer: 200000, windowsHide: true, shell: false });
      JSON.parse(stdout);
      return { output: stdout.trim(), metadata: { scope: 'component-test', usesLLM: false } };
    } catch (e) { return { error: `Component harness failed: ${e.message}` }; }
  }
}
