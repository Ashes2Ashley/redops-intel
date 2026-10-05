<!--B2PANELS-->
<div class="panel"><div class="panel-head"><span>Email Permutator</span><span class="tag">new</span></div>
<p class="fine">~16 likely addresses for a name — each with an exact-search link.</p>
<input id="ep_name" placeholder="Full name, e.g. John Doe">
<input id="ep_domain" placeholder="domain.com (optional)">
<button class="btn btn-primary" onclick="epGo()">Generate</button>
<div id="ep_out" style="margin-top:10px"></div></div>

<div class="panel"><div class="panel-head"><span>EXIF GPS Reader</span><span class="tag">new</span></div>
<p class="fine">Pull embedded GPS coordinates out of a photo's EXIF data (JPEG).</p>
<input id="ex_file" type="file" accept="image/jpeg">
<button class="btn btn-primary" onclick="exGo()">Read EXIF</button>
<div id="ex_out" style="margin-top:10px"></div></div>

<div class="panel"><div class="panel-head"><span>Platform Linker</span><span class="tag">new</span></div>
<p class="fine">One username → profile links across 9 platforms. Links only, not verification.</p>
<input id="pl_user" placeholder="username">
<button class="btn btn-primary" onclick="plGo()">Link</button>
<div id="pl_out" style="margin-top:10px"></div></div>

<div class="panel"><div class="panel-head"><span>Subdomain Enumerator</span><span class="tag">new</span></div>
<p class="fine">Pull subdomains from certificate transparency logs (source: crt.sh).</p>
<input id="sd_domain" placeholder="example.com">
<button class="btn btn-primary" onclick="sdGo()">Enumerate</button>
<div id="sd_out" style="margin-top:10px"></div></div>

<div class="panel"><div class="panel-head"><span>RTP Auditor</span><span class="tag">new</span></div>
<p class="fine">Chi-square check: does a set of outcomes match an expected win rate?</p>
<textarea id="rtp_obs" rows="5" placeholder="One outcome per line: 1/0 or w/l"></textarea>
<input id="rtp_exp" value="96" placeholder="Expected win % (e.g. 96)">
<button class="btn btn-primary" onclick="rtpGo()">Audit</button>
<div id="rtp_out" style="margin-top:10px"></div></div>

<div class="panel"><div class="panel-head"><span>Withdrawal Stalling Analyzer</span><span class="tag">new</span></div>
<p class="fine">Request/paid dates in → delay stats and &gt;7-day stalls out.</p>
<textarea id="ws_in" rows="5" placeholder="request_date,paid_date,amount (one per line, ISO dates)"></textarea>
<button class="btn btn-primary" onclick="wsGo()">Analyze</button>
<div id="ws_out" style="margin-top:10px"></div></div>

<div class="panel"><div class="panel-head"><span>Canary Tokens</span><span class="tag">new</span></div>
<p class="fine">Mint unique tripwire IDs; log a trip when one gets touched.</p>
<input id="ct_label" placeholder="Label, e.g. decoy admin doc">
<button class="btn btn-primary" onclick="ctGo()">Mint canary</button>
<div id="ct_out" style="margin-top:10px"></div></div>

<!--B2JS-->
function epGo(){
  var rawDom = document.getElementById('ep_domain').value.trim();
  var dom = rawDom.toLowerCase().replace(/[^a-z0-9.\-]/g,'') || 'gmail.com';
  var name = document.getElementById('ep_name').value.trim().toLowerCase().replace(/[^a-z\s'-]/g,'');
  var out = document.getElementById('ep_out');
  var parts = name.split(/\s+/).filter(function(x){return x;});
  if(parts.length < 2){ out.innerHTML = '<p class="fine">Enter a full name (first + last).</p>'; return; }
  var first = parts[0].replace(/['-]/g,''), last = parts[parts.length-1].replace(/['-]/g,'');
  if(!first || !last){ out.innerHTML = '<p class="fine">Could not parse a usable first/last name.</p>'; return; }
  var f = first.charAt(0), l = last.charAt(0);
  var locals = [first+'.'+last, f+last, first+last, first+'_'+last, f+'_'+last,
                last+'.'+first, l+first, last+first, first+l, f+'.'+last,
                first+'.'+l, last+'_'+first, f+l+last, first+'-'+last, last+'-'+first, f+'.'+l+last];
  var seen = {}, rows = [];
  locals.forEach(function(x){ if(!seen[x]){ seen[x]=1; rows.push(x); } });
  var h = '<p class="fine">Domain: <b>'+esc(dom)+'</b>'+(rawDom ? '' : ' <span class="fine">(guess — blank defaulted to gmail.com)</span>')+'</p>';
  rows.forEach(function(x){
    var addr = x + '@' + dom;
    h += '<div style="margin:4px 0"><b>'+esc(addr)+'</b> <a target="_blank" rel="noopener" href="https://www.google.com/search?q='+encodeURIComponent('"'+addr+'"')+'">exact search</a></div>';
  });
  out.innerHTML = h;
}
function exReadU16(dv, off, le){ return dv.getUint16(off, le); }
function exReadU32(dv, off, le){ return dv.getUint32(off, le); }
function exEntry(dv, ifd, want, le){
  var n = exReadU16(dv, ifd, le);
  for(var i=0;i<n;i++){
    var e = ifd + 2 + i*12;
    if(e+12 > dv.byteLength) break;
    if(exReadU16(dv, e, le) === want){
      return { type: exReadU16(dv, e+2, le), count: exReadU32(dv, e+4, le), val: exReadU32(dv, e+8, le) };
    }
  }
  return null;
}
function exAsciiRef(dv, ifd, want, le){
  var en = exEntry(dv, ifd, want, le);
  if(!en || en.type !== 2) return null;
  var v = en.val;
  return String.fromCharCode(le ? (v & 0xFF) : ((v >>> 24) & 0xFF));
}
function exRationalTriple(dv, ifd, want, le, tiff){
  var en = exEntry(dv, ifd, want, le);
  if(!en || en.type !== 5 || en.count < 3) return null;
  var base = tiff + en.val, out = [];
  for(var i=0;i<3;i++){
    if(base + i*8 + 8 > dv.byteLength) return null;
    var num = exReadU32(dv, base+i*8, le), den = exReadU32(dv, base+i*8+4, le);
    if(den === 0) return null;
    out.push(num/den);
  }
  return out;
}
function exParse(dv){
  var len = dv.byteLength, tiff = -1, i;
  for(i=0;i<len-6;i++){
    if(dv.getUint8(i)===0x45 && dv.getUint8(i+1)===0x78 && dv.getUint8(i+2)===0x69 &&
       dv.getUint8(i+3)===0x66 && dv.getUint8(i+4)===0 && dv.getUint8(i+5)===0){ tiff = i+6; break; }
  }
  if(tiff < 0) return { error: 'No EXIF data found in this image.' };
  var bo = exReadU16(dv, tiff, false), le;
  if(bo === 0x4949) le = true; else if(bo === 0x4D4D) le = false;
  else return { error: 'Not a valid TIFF header (bad byte order).' };
  if(exReadU16(dv, tiff+2, le) !== 42) return { error: 'Not a valid TIFF header (bad magic).' };
  var ifd0 = tiff + exReadU32(dv, tiff+4, le);
  if(ifd0+2 > len) return { error: 'Truncated EXIF (IFD0 out of range).' };
  var gpsPtr = exEntry(dv, ifd0, 0x8825, le);
  if(!gpsPtr) return { error: 'EXIF found, but no GPS IFD (tag 0x8825) — this photo has no location data.' };
  var gpsIfd = tiff + gpsPtr.val;
  if(gpsIfd+2 > len) return { error: 'Truncated EXIF (GPS IFD out of range).' };
  var latRef = exAsciiRef(dv, gpsIfd, 0x0001, le);
  var lonRef = exAsciiRef(dv, gpsIfd, 0x0003, le);
  var lat = exRationalTriple(dv, gpsIfd, 0x0002, le, tiff);
  var lon = exRationalTriple(dv, gpsIfd, 0x0004, le, tiff);
  if(!lat || !lon) return { error: 'GPS IFD present, but latitude/longitude tags are missing.' };
  var dLat = lat[0] + lat[1]/60 + lat[2]/3600; if(latRef === 'S') dLat = -dLat;
  var dLon = lon[0] + lon[1]/60 + lon[2]/3600; if(lonRef === 'W') dLon = -dLon;
  return { lat: dLat, lon: dLon };
}
function exGo(){
  var out = document.getElementById('ex_out');
  var f = document.getElementById('ex_file').files[0];
  if(!f){ out.innerHTML = '<p class="fine">Choose a JPEG first.</p>'; return; }
  out.innerHTML = '<p class="fine">Reading EXIF…</p>';
  var r = new FileReader();
  r.onload = function(){
    try{
      var res = exParse(new DataView(r.result));
      if(res.error){ out.innerHTML = '<p class="fine">'+esc(res.error)+'</p>'; }
      else{
        var q = res.lat.toFixed(6) + ',' + res.lon.toFixed(6);
        out.innerHTML = '<p>GPS: <b>'+esc(q)+'</b></p>' +
          '<a class="btn" target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query='+encodeURIComponent(q)+'">Open in Google Maps</a>';
      }
    }catch(e){ out.innerHTML = '<p class="fine">Parse error: '+esc(String((e && e.message) || e))+'</p>'; }
  };
  r.onerror = function(){ out.innerHTML = '<p class="fine">Could not read the file.</p>'; };
  r.readAsArrayBuffer(f);
}
function plGo(){
  var u = document.getElementById('pl_user').value.trim();
  var out = document.getElementById('pl_out');
  if(!u){ out.innerHTML = '<p class="fine">Enter a username.</p>'; return; }
  var e = encodeURIComponent(u);
  var links = [
    ['Steam','https://steamcommunity.com/id/'+e],
    ['Xbox','https://xboxgamertag.com/search/'+e],
    ['PSN','https://psnprofiles.com/'+e],
    ['Twitch','https://www.twitch.tv/'+e],
    ['Reddit','https://www.reddit.com/user/'+e],
    ['GitHub','https://github.com/'+e],
    ['X','https://x.com/'+e],
    ['TikTok','https://www.tiktok.com/@'+e],
    ['YouTube','https://www.youtube.com/@'+e]
  ];
  out.innerHTML = '<p class="fine">Profile links for <b>'+esc(u)+'</b> — links only, not identity verification.</p>' +
    links.map(function(x){ return '<a class="btn" target="_blank" rel="noopener" href="'+x[1]+'">'+x[0]+'</a>'; }).join(' ');
}
function sdGo(){
  var d = document.getElementById('sd_domain').value.trim().toLowerCase().replace(/[^a-z0-9.\-]/g,'');
  var out = document.getElementById('sd_out');
  if(!d){ out.innerHTML = '<p class="fine">Enter a domain first.</p>'; return; }
  out.innerHTML = '<p class="fine">Querying crt.sh (certificate transparency logs)…</p>';
  fetch('https://crt.sh/?q=%25.'+encodeURIComponent(d)+'&output=json').then(function(r){
    if(!r.ok) throw new Error('HTTP '+r.status);
    return r.json();
  }).then(function(j){
    var seen = {}, list = [];
    (j || []).forEach(function(row){
      String(row.name_value || '').split('\n').forEach(function(n){
        n = n.trim().toLowerCase();
        if(!n || n.indexOf('*') >= 0 || seen[n]) return;
        seen[n] = 1; list.push(n);
      });
    });
    list.sort();
    var h = '<p><b>'+list.length+'</b> unique subdomains <span class="fine">(source: crt.sh certificate transparency logs)</span></p>' +
      '<div class="fine" style="max-height:260px;overflow:auto;border:1px solid var(--border);padding:8px;border-radius:6px">' +
      list.slice(0,100).map(function(x){ return esc(x); }).join('<br>') + '</div>';
    if(list.length > 100) h += '<p class="fine">Showing first 100 of '+list.length+'.</p>';
    out.innerHTML = h;
  }).catch(function(){
    out.innerHTML = '<p class="fine">crt.sh lookup failed (network or blocked). Try these instead:</p>' +
      '<a class="btn" target="_blank" rel="noopener" href="https://crt.sh/?q=%25.'+encodeURIComponent(d)+'">crt.sh search</a> ' +
      '<a class="btn" target="_blank" rel="noopener" href="https://securitytrails.com/domain/'+encodeURIComponent(d)+'/dns">SecurityTrails</a>';
  });
}
function rtpGo(){
  var out = document.getElementById('rtp_out');
  var exp = parseFloat(document.getElementById('rtp_exp').value);
  if(isNaN(exp) || exp <= 0 || exp >= 100){ out.innerHTML = '<p class="fine">Expected win % must be between 0 and 100.</p>'; return; }
  var n = 0, wins = 0, bad = 0;
  document.getElementById('rtp_obs').value.split('\n').forEach(function(line){
    var v = line.trim().toLowerCase();
    if(!v) return;
    n++;
    if(v==='1' || v==='w' || v==='win') wins++;
    else if(v==='0' || v==='l' || v==='loss'){}
    else bad++;
  });
  if(n === 0){ out.innerHTML = '<p class="fine">Paste one outcome per line first (1/0 or w/l).</p>'; return; }
  if(bad){ out.innerHTML = '<p class="fine">'+bad+' line(s) not recognized — use 1/0 or w/l only.</p>'; return; }
  var p = exp/100, ew = n*p, el = n*(1-p), ow = wins, ol = n-wins;
  var chi = (ow-ew)*(ow-ew)/ew + (ol-el)*(ol-el)/el;
  var sig = chi > 3.84;
  out.innerHTML = '<p>n=<b>'+n+'</b> · observed win <b>'+(ow/n*100).toFixed(2)+'%</b> · expected <b>'+exp+'%</b></p>' +
    '<p>&chi;&sup2; = <b>'+chi.toFixed(3)+'</b> (1 df, critical 3.84 at 5%)</p>' +
    '<p>'+(sig ? '<b style="color:var(--red)">Deviation is statistically significant at 5% — unlikely to be chance alone.</b>'
                  : '<b style="color:var(--green)">Deviation is NOT significant at 5% — within normal variance.</b>')+'</p>' +
    '<p class="fine">Assumes each line is one independent trial and 1/w counts as a win. Small samples can look "rigged" by luck alone.</p>';
}
function wsGo(){
  var out = document.getElementById('ws_out');
  var rows = document.getElementById('ws_in').value.split('\n').map(function(l){ return l.trim(); }).filter(function(l){ return l; });
  if(!rows.length){ out.innerHTML = '<p class="fine">Paste lines like:<br><code>2026-09-01,2026-09-03,150000000</code><br>(request_date, paid_date, amount — ISO dates)</p>'; return; }
  var data = [], bad = 0;
  rows.forEach(function(r){
    var p = r.split(',').map(function(x){ return x.trim(); });
    var d1 = Date.parse(p[0]), d2 = Date.parse(p[1]);
    if(p.length < 3 || isNaN(d1) || isNaN(d2)){ bad++; return; }
    data.push({ req: p[0], paid: p[1], amt: p[2], days: (d2-d1)/86400000 });
  });
  if(!data.length){ out.innerHTML = '<p class="fine">No valid rows. Format: request_date,paid_date,amount</p>'; return; }
  var days = data.map(function(x){ return x.days; }).sort(function(a,b){ return a-b; });
  var avg = days.reduce(function(a,b){ return a+b; }, 0) / days.length;
  var med = days.length % 2 ? days[(days.length-1)/2] : (days[days.length/2-1] + days[days.length/2]) / 2;
  var flagged = data.filter(function(x){ return x.days > 7; });
  var h = '<p>Rows: <b>'+data.length+'</b> · avg delay <b>'+avg.toFixed(1)+'d</b> · median <b>'+med.toFixed(1)+'d</b> · max <b>'+days[days.length-1].toFixed(1)+'d</b></p>';
  if(flagged.length){
    h += '<p><b style="color:var(--red)">'+flagged.length+' payout(s) stalled &gt;7 days:</b></p><div class="fine">' +
      flagged.map(function(x){ return esc(x.req+' → '+x.paid+' · '+x.days.toFixed(1)+'d · '+x.amt); }).join('<br>') + '</div>';
  } else h += '<p class="fine">No rows over 7 days.</p>';
  if(bad) h += '<p class="fine">'+bad+' row(s) skipped (bad format).</p>';
  out.innerHTML = h;
}
function ctNewId(){
  if(window.crypto && crypto.randomUUID) return crypto.randomUUID();
  var b = new Uint8Array(16);
  crypto.getRandomValues(b);
  b[6] = (b[6] & 15) | 64; b[8] = (b[8] & 63) | 128;
  var hex = Array.prototype.map.call(b, function(x){ return ('0'+x.toString(16)).slice(-2); }).join('');
  return hex.slice(0,8)+'-'+hex.slice(8,12)+'-'+hex.slice(12,16)+'-'+hex.slice(16,20)+'-'+hex.slice(20);
}
function ctLoad(){ try{ return JSON.parse(localStorage.getItem('redops_canary') || '[]'); }catch(e){ return []; } }
function ctSave(a){ localStorage.setItem('redops_canary', JSON.stringify(a)); }
function ctRender(){
  var out = document.getElementById('ct_out');
  if(!out) return;
  var a = ctLoad();
  var h = '<p class="fine">Place a canary ID where only an intruder would touch it (a fake admin file, a decoy doc). A trip means someone touched it.</p>';
  if(!a.length) h += '<p class="fine">No canaries yet.</p>';
  a.forEach(function(t){
    h += '<div style="border:1px solid var(--border);border-radius:6px;padding:8px;margin:6px 0">' +
      '<div><b>'+esc(t.id)+'</b></div>' +
      '<div class="fine">'+esc(t.label || '(no label)')+' · created '+esc(t.created)+' · trips: '+t.trips.length+'</div>' +
      (t.trips.length ? '<div class="fine">trips: '+t.trips.map(function(x){ return esc(x); }).join(', ')+'</div>' : '') +
      '<button class="btn btn-danger" onclick="ctTrip(\''+t.id+'\')">Log trip</button></div>';
  });
  out.innerHTML = h;
}
function ctTrip(id){
  var a = ctLoad();
  for(var i=0;i<a.length;i++) if(a[i].id === id){ a[i].trips.push(new Date().toISOString()); break; }
  ctSave(a); ctRender();
}
function ctGo(){
  var label = document.getElementById('ct_label').value.trim();
  var a = ctLoad();
  a.push({ id: ctNewId(), label: label, created: new Date().toISOString(), trips: [] });
  ctSave(a);
  document.getElementById('ct_label').value = '';
  ctRender();
}
document.addEventListener('DOMContentLoaded', ctRender);
