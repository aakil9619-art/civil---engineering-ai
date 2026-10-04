const CivilAuth={
  config:null,
  user:null,
  async init(){
    this.config=await fetch('/api/auth/config').then(r=>r.json());
    const box=document.querySelector('#authBox');
    if(!this.config.enabled){box.innerHTML='<button class="login-btn" disabled>📱 Login OTP — setup required</button>';return;}
    firebase.initializeApp(this.config);
    firebase.auth().onAuthStateChanged(async u=>{
      this.user=u;
      if(u){box.innerHTML='<span class="user-phone">📱 '+(u.phoneNumber||'Student')+'</span><button class="login-btn" id="logoutBtn">Logout</button>';document.querySelector('#logoutBtn').onclick=()=>firebase.auth().signOut();window.dispatchEvent(new Event('civil-auth-ready'));setTimeout(()=>{if(typeof renderStudentDashboard==="function"&&CivilAuth.user)renderStudentDashboard();},0);}
      else{box.innerHTML='<button class="login-btn" id="loginBtn">📱 Login with OTP</button>';document.querySelector('#loginBtn').onclick=()=>this.open();}
    });
  },
  open(){
    const modal=document.querySelector('#authModal'); modal.classList.add('show');
    document.querySelector('#otpStep').style.display='none'; document.querySelector('#phoneStep').style.display='block';
    document.querySelector('#phoneInput').focus();
    if(!this.recaptcha) this.recaptcha=new firebase.auth.RecaptchaVerifier('recaptcha-container',{size:'invisible'});
  },
  async sendOTP(){
    const phone=document.querySelector('#phoneInput').value.trim();
    if(!/^\+[1-9]\d{7,14}$/.test(phone)){document.querySelector('#authError').textContent='Enter your number with country code, e.g. +91XXXXXXXXXX';return;}
    try{
      document.querySelector('#authError').textContent='Sending OTP…';
      this.confirmation=await firebase.auth().signInWithPhoneNumber(phone,this.recaptcha);
      document.querySelector('#phoneStep').style.display='none';document.querySelector('#otpStep').style.display='block';document.querySelector('#otpInput').focus();document.querySelector('#authError').textContent='';
    }catch(e){document.querySelector('#authError').textContent=e.message||'Could not send OTP. Please try again.';this.recaptcha=null;}
  },
  async verifyOTP(){
    try{document.querySelector('#authError').textContent='Verifying…';await this.confirmation.confirm(document.querySelector('#otpInput').value.trim());this.close();}
    catch(e){document.querySelector('#authError').textContent=e.message||'Invalid OTP.';}
  },
  close(){document.querySelector('#authModal').classList.remove('show');},
  async headers(){
    if(!this.user) throw new Error('Please login first.');
    return {Authorization:'Bearer '+await this.user.getIdToken()};
  },
  async fetch(url,opts={}){
    const h=Object.assign({},opts.headers||{},await this.headers());
    return fetch(url,Object.assign({},opts,{headers:h}));
  }
};
async function authFetch(url,opts={}){return CivilAuth.fetch(url,opts);}
window.CivilAuth=CivilAuth;window.authFetch=authFetch;
document.addEventListener('DOMContentLoaded',()=>CivilAuth.init().catch(e=>{const b=document.querySelector('#authBox');if(b)b.innerHTML='<span class="auth-error">Login service unavailable</span>';}));
