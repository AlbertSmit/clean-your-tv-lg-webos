'use strict';
// Repair only known state paths; preserve contents and ownership, never follow links.
module.exports=function(directory,log){
 var fs=require('fs'),c=fs.constants||require('constants'),ok=true;
 function repair(path,mode,isDirectory,optional){
  var fd;
  try {
   fd=fs.openSync(path,c.O_RDONLY|c.O_NOFOLLOW|c.O_NONBLOCK);
   var stat=fs.fstatSync(fd);
   if(isDirectory?!stat.isDirectory():!stat.isFile())throw Error('unsafe-type');
   if((stat.mode&4095)!==mode)fs.fchmodSync(fd,mode);
   if((fs.fstatSync(fd).mode&4095)!==mode)throw Error('mode-mismatch');
   return true;
  }catch(e){
   if(optional&&e.code==='ENOENT')return true;
   ok=false;if(log)log({event:'state-permissions-error',target:isDirectory?'directory':path.slice(directory.length+1),reason:e.code||e.message});return false;
  }finally{if(fd!==undefined)fs.closeSync(fd);}
 }
 if(!repair(directory,504,true,false))return false; // 0770
 repair(directory+'/ssap-key.json',416,false,true); // 0640
 repair(directory+'/apps.json',420,false,true); // 0644
 return ok;
};
