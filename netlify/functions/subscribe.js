const https = require('https');

const RESEND_API_KEY = process.env.RESEND_API_KEY;
const NOTIFY_EMAIL  = process.env.NOTIFY_EMAIL || 'elsane.tiberini@gmail.com';
const FROM_EMAIL    = process.env.FROM_EMAIL   || 'CyberQuantic Weekly <contact@cyberquantic.com>';

function httpPost(hostname, path, headers, body) {
  return new Promise((resolve, reject) => {
    const buf = Buffer.from(JSON.stringify(body));
    const req = https.request({ hostname, path, method: 'POST',
      headers: { ...headers, 'Content-Length': buf.byteLength } }, res => {
      let d = ''; res.on('data', c => d += c); res.on('end', () => resolve({ status: res.statusCode, body: d }));
    });
    req.on('error', reject); req.write(buf); req.end();
  });
}

async function sendEmail(to, subject, html) {
  if (!RESEND_API_KEY) return;
  return httpPost('api.resend.com', '/emails',
    { 'Authorization': `Bearer ${RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    { from: FROM_EMAIL, to: [to], subject, html });
}

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: 'Method Not Allowed' };

  let email = '';
  try {
    const ct = event.headers['content-type'] || '';
    const data = ct.includes('application/json')
      ? JSON.parse(event.body)
      : Object.fromEntries(new URLSearchParams(event.body));
    email = data.email || '';
  } catch(e) {}

  if (!email || !email.includes('@')) {
    return { statusCode: 400, body: JSON.stringify({ error: 'Invalid email' }) };
  }

  await Promise.allSettled([
    // Confirm to subscriber
    sendEmail(email, '✅ Bienvenue dans CyberQuantic Weekly !',
      `<div style="font-family:sans-serif;max-width:560px;margin:0 auto;padding:40px 24px">
        <h2 style="color:#4F46E5">Bienvenue dans CyberQuantic Weekly ! 🎉</h2>
        <p>Vous recevrez chaque lundi l'essentiel de l'IA B2B européenne :</p>
        <ul style="margin:16px 0;padding-left:20px">
          <li>🎯 Use case de la semaine avec guide d'implémentation</li>
          <li>🏢 Entreprise EU IA à suivre</li>
          <li>🔌 API ou outil recommandé</li>
          <li>💡 Prompt métier prêt à l'emploi</li>
          <li>⚖️ Conseil EU AI Act pratique</li>
        </ul>
        <a href="https://cyberquantic-matcher.netlify.app" style="display:inline-block;background:linear-gradient(135deg,#4F46E5,#7C3AED);color:#fff;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:16px">Trouver mes use cases IA →</a>
        <p style="margin-top:32px;color:#94a3b8;font-size:13px">Pour vous désabonner, répondez à cet email avec "désabonnement".<br><strong style="color:#4F46E5">L'équipe CyberQuantic</strong></p>
      </div>`),
    // Notify admin
    sendEmail(NOTIFY_EMAIL, `📬 Nouveau subscriber CyberQuantic Weekly — ${email}`,
      `<h3>Nouveau subscriber !</h3><p><strong>Email:</strong> ${email}</p><p>Ajouter manuellement dans subscribers.json</p>`)
  ]);

  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
    body: JSON.stringify({ success: true, message: 'Inscription confirmée !' })
  };
};
