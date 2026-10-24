(() => {
  'use strict';
  // Public Firebase web-app identifiers; access is enforced by Firestore rules.
  const config={apiKey:'AIzaSyBVzfqjQ9ws3rjblYOiSs0NK7qpfyl0_wE',authDomain:'bioe-radar.firebaseapp.com',projectId:'bioe-radar',storageBucket:'bioe-radar.firebasestorage.app',messagingSenderId:'790864157367',appId:'1:790864157367:web:90dac5fe58bfcb675d4b32'};
  let state={status:'loading',user:null,feedback:Object.create(null),message:'Connecting to your account…'},sdk,auth,db,unsubscribe,generation=0;
  const listeners=new Set();
  const emit=patch=>{state={...state,...patch};listeners.forEach(fn=>fn(state));};
  const explain=error=>({
    'auth/popup-blocked':'Allow the Google sign-in popup, then try again.',
    'auth/popup-closed-by-user':'Sign-in was closed. You can try again.',
    'auth/unauthorized-domain':'This website is not yet authorized for Google sign-in.',
    'auth/network-request-failed':'Google sign-in could not connect. Check your network and retry.',
    'permission-denied':'Could not access your private feedback. Please sign out and sign in again.'
  }[error.code]||'Could not connect to your account. Check your network and reload.');
  const ready=(async()=>{
    try{
      const base='https://www.gstatic.com/firebasejs/13.1.0/';
      const [app,A,F]=await Promise.all([import(base+'firebase-app.js'),import(base+'firebase-auth.js'),import(base+'firebase-firestore.js')]);
      sdk={A,F};const instance=app.initializeApp(config);auth=A.getAuth(instance);db=F.getFirestore(instance);
      A.onAuthStateChanged(auth,user=>{
        const current=++generation;if(unsubscribe)unsubscribe();unsubscribe=null;
        emit({status:user?'syncing':'signed-out',user:user?{uid:user.uid,displayName:user.displayName||'Reader'}:null,feedback:Object.create(null),message:user?'Loading your private feedback…':'Sign in to save private feedback and sync across devices.'});
        if(!user)return;
        unsubscribe=F.onSnapshot(F.collection(db,'readers',user.uid,'feedback'),{includeMetadataChanges:true},snapshot=>{
          if(current!==generation)return;
          const feedback=Object.create(null);snapshot.forEach(doc=>{const entry=doc.data();feedback[entry.key]=entry;});
          emit({status:'signed-in',feedback,message:snapshot.metadata.hasPendingWrites?'Saving…':snapshot.metadata.fromCache?'Offline — changes will sync when connected.':'Synced across your devices.'});
        },error=>{if(current===generation)emit({status:'sync-error',feedback:Object.create(null),message:explain(error)});});
      },error=>emit({status:'error',user:null,feedback:Object.create(null),message:explain(error)}));
      return true;
    }catch(error){emit({status:'error',message:'Account services could not load. Check your network and reload; articles remain available.'});return false;}
  })();
  window.BioERadarAccount={
    subscribe(fn){listeners.add(fn);fn(state);return()=>listeners.delete(fn);},
    getState:()=>state,
    async signIn(){if(!await ready)return;try{const provider=new sdk.A.GoogleAuthProvider();provider.setCustomParameters({prompt:'select_account'});await sdk.A.signInWithPopup(auth,provider);}catch(error){emit({message:explain(error)});}},
    async signOut(){if(!await ready)return;try{await sdk.A.signOut(auth);}catch(error){emit({message:explain(error)});}},
    async save(entry){
      if(state.status!=='signed-in'||!auth.currentUser)return false;
      const user=auth.currentUser.uid,current=generation;
      const hash=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(entry.key));
      if(current!==generation||auth.currentUser?.uid!==user)return false;
      const id=Array.from(new Uint8Array(hash),x=>x.toString(16).padStart(2,'0')).join('');
      const record={key:entry.key,id:String(state.feedback[entry.key]?.id||entry.id||''),doi:String(entry.doi||''),title:entry.title,journal:entry.journal,signals:[...entry.signals],note:entry.note,updatedAt:sdk.F.serverTimestamp()};
      try{await sdk.F.setDoc(sdk.F.doc(db,'readers',user,'feedback',id),record);return true;}
      catch(error){if(current===generation)emit({message:'Feedback was not saved. '+explain(error)});return false;}
    }
  };
})();
