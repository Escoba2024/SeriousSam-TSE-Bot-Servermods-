import sys,json,time
sys.path.insert(0,'/srv/tse-frida-probe-20261111/lib/python3.12/site-packages')
import frida
pid=int(sys.argv[1]); session=None;script=None
try:
 session=frida.get_local_device().attach(pid)
 script=session.create_script('''
let calls=0,leaves=0,bad=0,listener=null;
rpc.exports={
 arm(){listener=Interceptor.attach(Process.mainModule.getExportByName('probe'),{
  onEnter(args){this.x=args[0].toUInt32();calls++;},
  onLeave(value){leaves++;if(value.toUInt32()!==this.x+1)bad++;}
 });return {pid:Process.id,armed:true};},
 drain(){return {calls,leaves,bad};},
 stop(){listener.detach();Interceptor.flush();return {calls,leaves,bad,detached:true};}
};''')
 script.load();armed=script.exports_sync.arm();assert armed=={'pid':pid,'armed':True}
 time.sleep(1)
 sample=script.exports_sync.drain();assert sample['calls']>=50 and sample['calls']==sample['leaves'] and sample['bad']==0
 final=script.exports_sync.stop();assert final['detached'] and final['bad']==0
 script.unload();script=None;session.detach();session=None
 print(json.dumps({'version':frida.__version__,'arm':armed,'sample':sample,'final':final,'unload_detach':'PASS'}))
finally:
 if script is not None:script.unload()
 if session is not None:session.detach()
