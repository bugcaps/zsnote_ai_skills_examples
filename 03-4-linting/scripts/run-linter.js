#!/usr/bin/env node
/**
 * 의존성 없이 동작하는 최소 정적 분석기 (JavaScript 대상).
 * 프로젝트에 eslint가 있다면 이 파일의 checkFile()을 `npx eslint --format unix` 호출로 바꿔 쓰세요.
 * 출력 형식과 종료 코드만 유지하면 SKILL.md는 고칠 필요가 없습니다.
 *
 * 사용법: node run-linter.js <파일> [파일...]
 * 출력:   LEVEL 파일:줄 [규칙] 메시지
 * 종료:   0 = ERROR 없음, 1 = ERROR 있음, 2 = 사용법 오류
 */
const fs = require('fs');
const { spawnSync } = require('child_process');

const MAX_FINDINGS = 50; // 에이전트 컨텍스트 보호: 이보다 많으면 잘라서 요약만 알립니다.
const MAX_LINE = 120;

const LINE_RULES = [
  { level: 'ERROR', id: 'no-debugger', test: /^\s*debugger\b/, msg: 'debugger 문이 남아 있습니다.' },
  { level: 'WARN', id: 'no-var', test: /(^|[;{(\s])var\s+[\w$]/, msg: "'var' 대신 'const' 또는 'let'을 사용하세요." },
  { level: 'WARN', id: 'eqeqeq', test: /[^=!<>]==[^=]|!=[^=]/, msg: "'=='/'!=' 대신 '==='/'!=='를 사용하세요." },
  { level: 'WARN', id: 'no-console', test: /\bconsole\.log\(/, msg: 'console.log가 남아 있습니다.' },
];

function checkFile(file) {
  const findings = [];
  if (/\.(c|m)?js$/.test(file)) {
    const r = spawnSync(process.execPath, ['--check', file], { encoding: 'utf8' });
    if (r.status !== 0) {
      const line = (r.stderr.match(/:(\d+)\n/) || [])[1] || '1';
      const msg = (r.stderr.match(/^(\w*Error: .*)$/m) || [])[1] || '구문 오류';
      findings.push({ level: 'ERROR', line: Number(line), id: 'syntax', msg });
    }
  }
  fs.readFileSync(file, 'utf8').split(/\r?\n/).forEach((text, i) => {
    const code = text.replace(/\/\/.*$/, '').replace(/(['"`])(?:\\.|(?!\1).)*\1/g, '""');
    for (const rule of LINE_RULES) {
      if (rule.test.test(code)) findings.push({ level: rule.level, line: i + 1, id: rule.id, msg: rule.msg });
    }
    if (text.length > MAX_LINE) {
      findings.push({ level: 'WARN', line: i + 1, id: 'max-len', msg: `한 줄이 ${MAX_LINE}자를 넘습니다 (${text.length}자).` });
    }
  });
  return findings.map((f) => ({ ...f, file }));
}

const files = process.argv.slice(2);
if (!files.length) {
  console.error('사용법: node run-linter.js <파일> [파일...]');
  process.exit(2);
}
const missing = files.filter((f) => !fs.existsSync(f));
if (missing.length) {
  console.error(`오류: 파일을 찾을 수 없습니다: ${missing.join(', ')}`);
  process.exit(2);
}

const all = files.flatMap(checkFile).sort((a, b) => (a.level === b.level ? 0 : a.level === 'ERROR' ? -1 : 1));
const errors = all.filter((f) => f.level === 'ERROR').length;
all.slice(0, MAX_FINDINGS).forEach((f) => console.log(`${f.level} ${f.file}:${f.line} [${f.id}] ${f.msg}`));
if (all.length > MAX_FINDINGS) console.log(`... 외 ${all.length - MAX_FINDINGS}건 생략 (ERROR 우선 정렬)`);
console.log(`요약: ERROR ${errors}건, WARN ${all.length - errors}건`);
process.exit(errors ? 1 : 0);
