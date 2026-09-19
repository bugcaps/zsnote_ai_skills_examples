#!/usr/bin/env node
/**
 * 번역 파일이 assets/glossary.json의 표기 규칙을 지키는지 검사합니다.
 * 의존성 없이 Node 표준 라이브러리만 사용합니다. 번역의 정확성은 판정하지 않습니다.
 *
 * 사용법: node check-l10n.js <원문.json> <번역.json> <로케일>
 *         원문·번역 파일은 같은 키를 쓰는 평평한 "키: 문자열" JSON입니다.
 * 출력:   LEVEL 키 [검사명] 메시지
 * 종료:   0 = ERROR 없음, 1 = ERROR 있음, 2 = 사용법 오류
 */
const fs = require('fs');
const path = require('path');

const MAX_FINDINGS = 50; // 에이전트 컨텍스트 보호: 이보다 많으면 잘라서 건수만 알립니다.
const GLOSSARY_PATH = path.join(__dirname, '..', 'assets', 'glossary.json');
const URL_RE = /https?:\/\/[^\s"'<>)\]}]+/g;

function die(msg) {
  console.error(msg);
  process.exit(2);
}

function readJson(file) {
  if (!fs.existsSync(file)) die(`오류: 파일을 찾을 수 없습니다: ${file}`);
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (e) {
    return die(`오류: JSON 형식이 올바르지 않습니다: ${file} (${e.message})`);
  }
}

const [srcFile, dstFile, locale] = process.argv.slice(2);
if (!srcFile || !dstFile || !locale) die('사용법: node check-l10n.js <원문.json> <번역.json> <로케일>');

const rules = readJson(GLOSSARY_PATH);
if (!rules.locales.includes(locale)) {
  die(`오류: '${locale}'은 glossary.json의 대상 로케일이 아닙니다. 가능한 값: ${rules.locales.join(', ')}`);
}
const source = readJson(srcFile);
const target = readJson(dstFile);
const placeholderRe = new RegExp(rules.placeholder_patterns.join('|'), 'g');

const list = (arr) => (arr.length ? arr.join(', ') : '없음');
const bag = (arr) => arr.slice().sort().join('\u0000');
const holders = (text) => text.match(placeholderRe) || [];
const urls = (text) => (text.match(URL_RE) || []).map((u) => u.replace(/[.,)\]]+$/, ''));
// 원문에 실제로 있는 항목만 검사하고, 더 긴 항목에 포함되는 항목은 중복 보고하지 않습니다.
function dntIn(text) {
  const hit = rules.do_not_translate.filter((t) => text.includes(t));
  return hit.filter((t) => !hit.some((other) => other !== t && other.includes(t)));
}

const findings = [];
const add = (level, key, id, msg) => findings.push({ level, key, id, msg });

for (const [key, src] of Object.entries(source)) {
  const dst = target[key];
  if (typeof dst !== 'string' || dst.trim() === '') {
    add('WARN', key, '빈-번역', typeof dst === 'string' ? '번역문이 비어 있습니다.' : '번역문에 이 항목이 없습니다.');
    continue;
  }
  if (dst === src) add('WARN', key, '미번역', '번역문이 원문과 완전히 같습니다. 의도한 것인지 확인하세요.');

  const [sHolders, dHolders] = [holders(src), holders(dst)];
  if (bag(sHolders) !== bag(dHolders)) {
    add('ERROR', key, '자리표시자', `자리표시자가 다릅니다. 원문 ${list(sHolders)} / 번역문 ${list(dHolders)}`);
  }
  for (const term of dntIn(src)) {
    if (!dst.includes(term)) add('ERROR', key, '번역금지', `'${term}'은 번역하지 않고 글자 그대로 두어야 합니다.`);
  }
  for (const entry of rules.glossary) {
    const want = entry[locale];
    if (!want || !src.includes(entry.source)) continue;
    if (!dst.toLowerCase().includes(want.toLowerCase())) {
      add('ERROR', key, '용어집', `'${entry.source}'의 ${locale} 대응어 '${want}'가 번역문에 없습니다.`);
    }
  }
  const [sUrls, dUrls] = [urls(src), urls(dst)];
  if (bag(sUrls) !== bag(dUrls)) {
    add('ERROR', key, 'URL', `URL이 다릅니다. 원문 ${list(sUrls)} / 번역문 ${list(dUrls)}`);
  }
}

const sorted = findings.sort((a, b) => (a.level === b.level ? 0 : a.level === 'ERROR' ? -1 : 1));
const errors = sorted.filter((f) => f.level === 'ERROR').length;
sorted.slice(0, MAX_FINDINGS).forEach((f) => console.log(`${f.level} ${f.key} [${f.id}] ${f.msg}`));
if (sorted.length > MAX_FINDINGS) console.log(`... 외 ${sorted.length - MAX_FINDINGS}건 생략 (ERROR 우선 정렬)`);
console.log(`요약: ${locale} / 문자열 ${Object.keys(source).length}개, ERROR ${errors}건, WARN ${sorted.length - errors}건`);
process.exit(errors ? 1 : 0);
