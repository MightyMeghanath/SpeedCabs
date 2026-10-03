from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Fix known malformed closing fragment from an earlier version.
s = s.replace('\n/div>\n<div class="monthly">', '\n</div>\n<div class="monthly">')

# Add a purpose selector to Quick Booking.
if 'id="purpose"' not in s:
    needle = '<div class="tripTabs"><button id="localTab" class="active" type="button">🏙️ Hyderabad Local</button><button id="outstationTab" type="button">🛣️ Outstation</button></div>'
    repl = needle + '\n<div class="fields"><label>Purpose / journey type*<select id="purpose" name="purpose" required><option value="">Choose purpose</option><option>Local Hyderabad</option><option>Airport Transfer</option><option>Outstation Cab</option><option>Corporate & Events</option></select></label></div>'
    s = s.replace(needle, repl, 1)

# Make service choices select a purpose rather than navigating away.
s = s.replace('<a href="#booking">Book a local ride →</a>', '<a href="#booking" data-purpose="Local Hyderabad">Book a local ride →</a>')
s = s.replace('<a href="#booking">Request airport fare →</a>', '<a href="#booking" data-purpose="Airport Transfer">Request airport fare →</a>')
s = s.replace('<a href="#routes">Explore routes →</a>', '<a href="#booking" data-purpose="Outstation Cab">Explore routes →</a>')
s = s.replace('<a href="#booking">Enquire now →</a>', '<a href="#booking" data-purpose="Corporate & Events">Enquire now →</a>')

# Direct-call CTAs.
s = s.replace('<a class="btn primary" href="#booking">Get exact fare →</a>', '<a class="btn primary" href="tel:+917702506490">Get exact fare →</a>')
s = s.replace('<span class="priceAsk">Price on request →</span>', '<a class="priceAsk" href="tel:+917702506490">Price on request →</a>')
s = s.replace('href="mailto:speedcabs770@gmail.com?subject=SpeedCabs%20Monthly%20Package%20Enquiry"', 'href="tel:+917702506490"')

# Give monthly fields names for the SMS function.
field_map = {
    '<label>Name*<input required placeholder="Your name">': '<label>Name*<input name="name" required placeholder="Your name">',
    '<label>Phone*<input required type="tel" placeholder="10-digit mobile number">': '<label>Phone*<input name="phone" required type="tel" placeholder="10-digit mobile number">',
    '<label>Email<input type="email" placeholder="you@example.com">': '<label>Email<input name="email" type="email" placeholder="you@example.com">',
    '<label>Company / Organisation<input placeholder="Company name (optional)">': '<label>Company / Organisation<input name="company" placeholder="Company name (optional)">',
    '<label>Preferred vehicle<select>': '<label>Preferred vehicle<select name="vehicle">',
    '<label>Days per month<input placeholder="e.g. 22">': '<label>Days per month<input name="days" placeholder="e.g. 22">',
    '<label>Approx. hours per day<input placeholder="e.g. 8">': '<label>Approx. hours per day<input name="hours" placeholder="e.g. 8">',
    '<label>Pickup area<input placeholder="e.g. Banjara Hills">': '<label>Pickup area<input name="pickup" placeholder="e.g. Banjara Hills">',
    '<label>Destination / route<input placeholder="e.g. Office commute / multiple routes">': '<label>Destination / route<input name="destination" placeholder="e.g. Office commute / multiple routes">',
}
for a,b in field_map.items():
    s = s.replace(a,b,1)

# Booking form: show the existing confirmation modal, then notify securely via Netlify Function.
old = """   modal.style.display='flex'; document.body.style.overflow='hidden';\n   status.textContent='Your request is received. Notification delivery will be confirmed by the booking system.';\n   status.textContent='Your request is received. You can send the booking details to SpeedCabs on WhatsApp or call us now.';"""
new = """   modal.style.display='flex'; document.body.style.overflow='hidden';\n   status.textContent='Sending your confirmation message…';\n   try{\n     const response=await fetch('/.netlify/functions/notify-booking',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});\n     if(!response.ok) throw new Error('SMS service unavailable');\n     status.textContent='Thank you! We received your request and sent confirmation messages. We will contact you shortly.';\n   }catch(err){\n     status.textContent='Thank you! We received your request. We will contact you shortly. For immediate assistance, call 7702506490.';\n   }"""
s = s.replace(old,new,1)

# Purpose behavior for service cards.
needle = " localTab.onclick=()=>show('local'); outTab.onclick=()=>show('outstation');"
if 'data-purpose' not in s[s.find(needle):s.find(needle)+2600]:
    addition = needle + "\n document.querySelectorAll('[data-purpose]').forEach(a=>a.addEventListener('click',()=>{const p=document.getElementById('purpose');p.value=a.dataset.purpose;if(a.dataset.purpose==='Outstation Cab')show('outstation');else show('local');}));\n const purpose=document.getElementById('purpose'); if(purpose) purpose.addEventListener('change',()=>{if(purpose.value==='Outstation Cab')show('outstation');else show('local');});"
    s = s.replace(needle, addition,1)

# Monthly form: confirmation plus secure SMS function.
if 'notify-monthly' not in s:
    marker = " document.getElementById('closeSuccess').onclick="
    handler = """ const monthlyForm=document.getElementById('monthlyForm');\n if(monthlyForm){monthlyForm.addEventListener('submit',async function(e){e.preventDefault();const d=Object.fromEntries(new FormData(monthlyForm).entries());const box=document.getElementById('monthlySuccess');box.style.display='block';box.textContent='Thank you! Your monthly enquiry has been received. Sending confirmation…';try{const r=await fetch('/.netlify/functions/notify-monthly',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});if(!r.ok)throw new Error();box.textContent='Thank you! Your monthly enquiry has been received. We will contact you shortly. Confirmation messages were sent.';}catch(err){box.innerHTML='Thank you! Your monthly enquiry has been received. We will contact you shortly. For immediate assistance, call <a href=\"tel:+917702506490\">7702506490</a>.';}});}\n"""
    s = s.replace(marker, handler + marker,1)

p.write_text(s, encoding='utf-8')
