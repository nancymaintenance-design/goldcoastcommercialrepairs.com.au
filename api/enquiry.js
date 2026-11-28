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

function customerReceipt(from, form) {
  const chinese = form.language === 'zh';
  const phone = '0450 666 876';
  const paragraphs = chinese
    ? [
      '您好，感谢您联系 Ellis Gold Coast。我们已收到您的商业物业维修咨询，会先查看您提供的物业信息和维修事项，再与您沟通下一步安排。',
      `我们的维修团队经常在现场作业，邮件可能无法及时查阅。如需尽快与我们沟通，请直接致电 Ellis：${phone}。`,
      '来电时，您可以告诉我们物业所在区域和需要处理的问题，方便我们了解现场情况。',
      'Ellis Gold Coast 客服团队'
    ]
    : [
      'Thank you for contacting Ellis Gold Coast. We’ve received your commercial property maintenance enquiry and will review the details you provided before getting in touch about the next steps.',
      `Our maintenance team is often on site and may not be able to check email promptly. If you’d like to speak with us sooner, please call Ellis directly on ${phone}.`,
      'When you call, please let us know the property’s suburb and briefly describe what needs attention.',
      'Ellis Gold Coast Customer Service'
    ];
  // Keep the receipt copy fixed so the form cannot relay user-provided text to third parties.
  const html = paragraphs.map(paragraph => '<p>' + paragraph.replace(
    phone, '<a href="tel:+61450666876">' + phone + '</a>'
  ) + '</p>').join('');
  return {
    from, to: [form.email], reply_to: RECIPIENT,
    subject: chinese ? '已收到您的维修咨询｜Ellis Gold Coast' : 'We’ve received your enquiry | Ellis Gold Coast',
    text: paragraphs.join('\n\n'),
    html: `<!doctype html><html lang="${chinese ? 'zh-Hans' : 'en-AU'}"><body>${html}</body></html>`
  };
}

async function sendEmail(apiKey, key, stage, payload, timeout) {
  try {
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: 'Bearer ' + apiKey,
        'Content-Type': 'application/json',
        'Idempotency-Key': 'gold-coast-' + stage + '/' + key
      },
      redirect: 'error',
      signal: AbortSignal.timeout(timeout),
      body: JSON.stringify(payload)
    });
    if (response.ok && typeof (await response.json()).id === 'string') return true;
    console.warn('Gold Coast email rejected by mail provider', stage, response.status);
  } catch {
    console.warn('Gold Coast email provider request failed', stage);
  }
  return false;
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
  const accepted = await sendEmail(apiKey, key, 'enquiry', {
    from, to: [RECIPIENT], reply_to: form.email,
    subject: 'Ellis Gold Coast — Website enquiry', text: emailText(form)
  }, 10000);
  if (!accepted) return res.status(502).json({ accepted: false });

  await sendEmail(apiKey, key, 'receipt', customerReceipt(from, form), 3500);
  return res.status(202).json({ accepted: true });
}

module.exports = enquiry;
