const content = require('../src/content.json');

const RECIPIENT = 'melbournecommercialrepairs.au@outlook.com';
const BODY_LIMIT = 24_000;
const MAX_LENGTH = {
  name: 100, email: 200, suburb: 100, property: 80, service: 80,
  article: 100, accessWindow: 200, message: 6000, website: 200, language: 2
};
const REQUIRED = ['name', 'email', 'suburb', 'property', 'message'];
const OPTIONS = Object.fromEntries(['sectors', 'services', 'articles'].map(key => [
  key, new Map(content[key].map(({ slug, title }) => [slug, title]))
]));

function sameOrigin(headers) {
  try {
    const origin = new URL(headers.origin);
    return origin.host === headers.host
      && (origin.protocol === 'https:'
        || (origin.protocol === 'http:' && ['localhost', '127.0.0.1'].includes(origin.hostname)));
  } catch {
    return false;
  }
}

function emailText(form) {
  const language = form.language === 'zh' ? 'zh' : 'en';
  const labels = language === 'zh'
    ? ['姓名', '邮箱', '地区', '物业类型', '服务项目', '相关指南', '期望的进场时段', '需要处理的事项']
    : ['Name', 'Email', 'Suburb', 'Property type', 'Service', 'Related guide', 'Preferred access window', 'Work required'];
  return [
    'Ellis Gold Coast — Website enquiry', '',
    ...[
      form.name, form.email, form.suburb, OPTIONS.sectors.get(form.property)[language],
      OPTIONS.services.get(form.service)?.[language],
      OPTIONS.articles.get(form.article)?.[language], form.accessWindow
    ].flatMap((value, index) => value ? ['' + labels[index] + ': ' + value] : []),
    '', labels[7] + ':', form.message
  ].join('\n');
}

async function enquiry(req, res) {
  const headers = req.headers || {};
  res.setHeader('Cache-Control', 'no-store');
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ accepted: false });
  }
  if (!sameOrigin(headers)) return res.status(403).json({ accepted: false });
  if (!/^application\/json(?:\s*;|$)/i.test(headers['content-type'] || '')) {
    return res.status(415).json({ accepted: false });
  }
  if (Number(headers['content-length']) > BODY_LIMIT) {
    return res.status(413).json({ accepted: false });
  }
  const key = headers['idempotency-key'];
  if (typeof key !== 'string' || !/^[a-f\d]{8}(?:-[a-f\d]{4}){3}-[a-f\d]{12}$/i.test(key)) {
    return res.status(400).json({ accepted: false });
  }

  const body = req.body;
  if (!body || typeof body !== 'object' || Array.isArray(body)) {
    return res.status(400).json({ accepted: false });
  }
  if (Buffer.byteLength(JSON.stringify(body)) > BODY_LIMIT) {
    return res.status(413).json({ accepted: false });
  }
  const form = {};
  for (const [name, limit] of Object.entries(MAX_LENGTH)) {
    const value = body[name] ?? '';
    if (typeof value !== 'string' || value.length > limit) {
      return res.status(400).json({ accepted: false });
    }
    form[name] = value.trim();
  }
  if (form.website
    || REQUIRED.some(name => !form[name])
    || !/^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(form.email)
    || !OPTIONS.sectors.has(form.property)
    || (form.service && !OPTIONS.services.has(form.service))
    || (form.article && !OPTIONS.articles.has(form.article))) {
    return res.status(400).json({ accepted: false });
  }

  const apiKey = process.env.RESEND_API_KEY;
  const from = process.env.RESEND_FROM_EMAIL;
  if (!apiKey || !from) return res.status(503).json({ accepted: false });
  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer ' + apiKey,
        'Content-Type': 'application/json',
        'Idempotency-Key': 'gold-coast-enquiry/' + key
      },
      redirect: 'error',
      signal: AbortSignal.timeout(10000),
      body: JSON.stringify({
        from, to: [RECIPIENT], reply_to: form.email,
        subject: 'Ellis Gold Coast — Website enquiry', text: emailText(form)
      })
    });
    if (response.ok && typeof (await response.json()).id === 'string') {
      return res.status(202).json({ accepted: true });
    }
    console.warn('Gold Coast enquiry rejected by mail provider', response.status);
  } catch {
    console.warn('Gold Coast enquiry provider request failed');
  }
  return res.status(502).json({ accepted: false });
}

module.exports = enquiry;
