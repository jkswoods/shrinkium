package dev.shrinkium;
import com.hypixel.hytale.codec.*;
import com.hypixel.hytale.codec.builder.BuilderCodec;
import com.hypixel.hytale.component.*;
import com.hypixel.hytale.protocol.packets.interface_.*;
import com.hypixel.hytale.server.core.entity.entities.Player;
import com.hypixel.hytale.server.core.entity.entities.player.pages.InteractiveCustomUIPage;
import com.hypixel.hytale.server.core.ui.builder.*;
import com.hypixel.hytale.server.core.universe.PlayerRef;
import com.hypixel.hytale.server.core.universe.world.storage.EntityStore;
final class RayPage extends InteractiveCustomUIPage<RayPage.Action>{
    public static final class Action{String action="";static final BuilderCodec<Action>CODEC=BuilderCodec.builder(Action.class,Action::new).append(new KeyedCodec<>("Action",Codec.STRING),(a,v)->a.action=v,a->a.action).add().build();}
    boolean dismissed;
    RayPage(PlayerRef p){super(p,CustomPageLifetime.CanDismiss,Action.CODEC);}
    static void open(Store<EntityStore>s,Ref<EntityStore>r){if(!ShrinkiumPlugin.held(s,r)){ShrinkiumPlugin.message(s,r,"Hold your Shrink Ray to choose its size. /shrinkium restore always works without it.");return;}s.getComponent(r,Player.getComponentType()).getPageManager().openCustomPage(r,s,new RayPage(s.getComponent(r,PlayerRef.getComponentType())));}
    @Override public void build(Ref<EntityStore>r,UICommandBuilder c,UIEventBuilder e,Store<EntityStore>s){c.append("Pages/Shrinkium/Ray.ui");float f=ShrinkiumPlugin.settings(s,r).factor;for(String id:new String[]{"75","50","25","100","Self","Close"})e.addEventBinding(CustomUIEventBindingType.Activating,"#B"+id,EventData.of("Action",id),false);c.set("#Selected.Text",f==1?"SELECTED: RESTORE ORIGINAL":"SELECTED: "+Math.round(f*100)+"%");}
    @Override public void handleDataEvent(Ref<EntityStore>r,Store<EntityStore>s,Action a){s.getExternalData().getWorld().execute(()->{if(dismissed||!r.isValid()||r.getStore()!=s)return;var p=s.getComponent(r,Player.getComponentType());if(p==null||p.getPageManager().getCustomPage()!=this)return;if(a.action.equals("Close")){dismissed=true;close();return;}if(!ShrinkiumPlugin.held(s,r)){dismissed=true;close();return;}if(a.action.equals("Self")){dismissed=true;close();ShrinkiumPlugin.fire(s,r,true,false);return;}float f=switch(a.action){case "75"->.75f;case "50"->.5f;case "25"->.25f;case "100"->1f;default->0;};if(!ShrinkRules.choice(f))return;ShrinkiumPlugin.settings(s,r).factor=f;ShrinkiumPlugin.cue(s,"Select",NativeGeometry.eye(s,r));var c=new UICommandBuilder();c.set("#Selected.Text",f==1?"SELECTED: RESTORE ORIGINAL":"SELECTED: "+Math.round(f*100)+"%");sendUpdate(c,null,false);});}
    @Override public void onDismiss(Ref<EntityStore>r,Store<EntityStore>s){dismissed=true;}
}
