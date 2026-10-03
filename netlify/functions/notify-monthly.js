exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return { statusCode: 405, body: 'Method Not Allowed' };
  try {
    const data = JSON.parse(event.body || '{}');
    return await sendNotifications(data);
  } catch (e) {
    return { statusCode: 400, body: JSON.stringify({ ok:false, error:'Invalid request' }) };
  }
};

async function sendNotifications(data) {
  const required = ['TWILIO_ACCOUNT_SID','TWILIO_AUTH_TOKEN','TWILIO_FROM_NUMBER','OWNER_PHONE'];
  const missing = required.filter(k => !process.env[k]);
  if (missing.length) return { statusCode: 503, body: JSON.stringify({ ok:false, error:'SMS provider is not configured', missing }) };

  const customer = normalizePhone(data.phone);
  const owner = normalizePhone(process.env.OWNER_PHONE);
  if (!customer || !owner) return { statusCode: 400, body: JSON.stringify({ ok:false, error:'Valid customer and owner phones are required' }) };

  const ownerMsg = `SpeedCabs monthly enquiry received. Name: ${data.name || ''}. Pickup: ${data.pickup || ''}. Route: ${data.destination || ''}. Vehicle: ${data.vehicle || ''}. Days: ${data.days || ''}. Hours/day: ${data.hours || ''}. Phone: ${data.phone || ''}.`;
  const customerMsg = `Thank you ${data.name || ''}. SpeedCabs Hyderabad received your monthly package enquiry. We will contact you shortly. Call 7702506490 for urgent help.`;
  const results = await Promise.all([twilioSend(owner, ownerMsg), twilioSend(customer, customerMsg)]);
  if (results.some(r => !r.ok)) return { statusCode: 502, body: JSON.stringify({ ok:false, error:'One or more SMS messages failed' }) };
  return { statusCode: 200, body: JSON.stringify({ ok:true }) };
}

function normalizePhone(v){
  const raw = String(v || '').replace(/[^0-9+]/g,'');
  if (!raw) return '';
  if (raw.startsWith('+')) return raw;
  if (/^[6-9][0-9]{9}$/.test(raw)) return '+91' + raw;
  return raw;
}

async function twilioSend(to, body){
  const auth = Buffer.from(`${process.env.TWILIO_ACCOUNT_SID}:${process.env.TWILIO_AUTH_TOKEN}`).toString('base64');
  const params = new URLSearchParams({To:to, From:process.env.TWILIO_FROM_NUMBER, Body:body});
  const r = await fetch(`https://api.twilio.com/2010-04-01/Accounts/${process.env.TWILIO_ACCOUNT_SID}/Messages.json`,{method:'POST',headers:{Authorization:`Basic ${auth}`,'Content-Type':'application/x-www-form-urlencoded'},body:params});
  return {ok:r.ok};
}
