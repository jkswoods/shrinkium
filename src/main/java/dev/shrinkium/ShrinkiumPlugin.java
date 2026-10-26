package dev.shrinkium;

import com.hypixel.hytale.component.*;
import com.hypixel.hytale.component.query.Query;
import com.hypixel.hytale.component.system.tick.EntityTickingSystem;
import com.hypixel.hytale.protocol.SoundCategory;
import com.hypixel.hytale.server.core.Message;
import com.hypixel.hytale.server.core.asset.type.soundevent.config.SoundEvent;
import com.hypixel.hytale.server.core.command.system.CommandContext;
import com.hypixel.hytale.server.core.command.system.basecommands.AbstractPlayerCommand;
import com.hypixel.hytale.server.core.entity.entities.Player;
import com.hypixel.hytale.server.core.inventory.ItemStack;
import com.hypixel.hytale.server.core.inventory.container.ItemContainer;
import com.hypixel.hytale.server.core.modules.entity.component.*;
import com.hypixel.hytale.server.core.modules.entity.damage.DeathComponent;
import com.hypixel.hytale.server.core.modules.entity.teleport.Teleport;
import com.hypixel.hytale.server.core.modules.interaction.interaction.config.Interaction;
import com.hypixel.hytale.server.core.plugin.*;
import com.hypixel.hytale.server.core.universe.PlayerRef;
import com.hypixel.hytale.server.core.universe.world.*;
import com.hypixel.hytale.server.core.universe.world.storage.EntityStore;
import com.hypixel.hytale.server.npc.entities.NPCEntity;
import org.joml.Vector3d;

public final class ShrinkiumPlugin extends JavaPlugin {
    static ShrinkiumPlugin instance;
    static ComponentType<EntityStore,ShrinkState> stateType;
    static ComponentType<EntityStore,RaySettings> settingsType;
    public ShrinkiumPlugin(JavaPluginInit init){super(init);}
    @Override protected void setup(){
        instance=this;stateType=getEntityStoreRegistry().registerComponent(ShrinkState.class,"ShrinkiumSizeV1",ShrinkState.CODEC);
        settingsType=getEntityStoreRegistry().registerComponent(RaySettings.class,"ShrinkiumSettingsV1",RaySettings.CODEC);
        getCodecRegistry(Interaction.CODEC).register("SH_Ray",RayInteraction.class,RayInteraction.CODEC);
        getEntityStoreRegistry().registerSystem(new Tick());getEntityStoreRegistry().registerSystem(new ShrinkSkinSync());
        getEventRegistry().registerGlobal(com.hypixel.hytale.server.core.universe.world.events.ChunkPreLoadProcessEvent.class,CrystalFeatures::column);
        getCommandRegistry().registerCommand(new Controls());
        if(Boolean.getBoolean("shrinkium.privateProbe"))try{Class.forName("dev.shrinkium.NativeProbe").getMethod("install",ShrinkiumPlugin.class).invoke(null,this);}catch(ReflectiveOperationException e){throw new IllegalStateException("Private probe absent",e);}
    }
    @Override protected void start(){getLogger().atInfo().log("Shrinkium private prototype loaded. Declared range >=0.7.4 <0.8.0. Native/human acceptance remains separate.");}
    static void message(Store<EntityStore>s,Ref<EntityStore>r,String text){var p=s.getComponent(r,PlayerRef.getComponentType());if(p!=null)p.sendMessage(Message.raw(text));}
    static boolean held(Store<EntityStore>s,Ref<EntityStore>r){var p=s.getComponent(r,Player.getComponentType());if(p==null)return false;var item=p.getInventory().getItemInHand();return item!=null&&"SH_Ray".equals(item.getItemId());}
    static RaySettings settings(Store<EntityStore>s,Ref<EntityStore>r){var c=s.getComponent(r,settingsType);if(c==null){c=new RaySettings();s.putComponent(r,settingsType,c);}if(!ShrinkRules.choice(c.factor))c.factor=.5f;return c;}
    static boolean eligible(Store<EntityStore>s,Ref<EntityStore>r){return r!=null&&r.isValid()&&r.getStore()==s&&s.getComponent(r,ModelComponent.getComponentType())!=null&&s.getComponent(r,BoundingBox.getComponentType())!=null&&s.getComponent(r,TransformComponent.getComponentType())!=null&&s.getComponent(r,DeathComponent.getComponentType())==null&&(s.getComponent(r,Player.getComponentType())!=null||s.getComponent(r,NPCEntity.getComponentType())!=null)&&s.getComponent(r,Teleport.getComponentType())==null;}
    static void cue(Store<EntityStore>s,String name,Vector3d at){var map=SoundEvent.getAssetMap();String id="SH_"+name;if(map.getAsset(id)!=null)SoundUtil.playSoundEvent3d(map.getIndex(id),SoundCategory.SFX,at,s);}
    static void beam(Store<EntityStore>s,Vector3d from,Vector3d end,boolean hit){int segments=Math.max(1,(int)Math.ceil(from.distance(end)/.18));for(int i=0;i<=segments;i++)ParticleUtil.spawnParticleEffect("SH_Beam",new Vector3d(from).lerp(end,(double)i/segments),s);if(hit)ParticleUtil.spawnParticleEffect("SH_Impact",end,s);}
    static void fire(Store<EntityStore>s,Ref<EntityStore>actor,boolean self,boolean emergency){
        s.assertThread();if(!eligible(s,actor)||(!emergency&&!held(s,actor)))return;
        var options=settings(s,actor);long now=System.nanoTime();if(!emergency&&now<options.nextShot)return;options.nextShot=now+1_000_000_000L;
        var hit=self?null:NativeGeometry.aim(s,actor);var target=self?actor:hit.target();
        if(!eligible(s,target)){if(hit!=null)beam(s,hit.start(),hit.end(),false);message(s,actor,"No visible living target. No crystal used.");return;}
        float factor=emergency?1:options.factor;var existing=s.getComponent(target,stateType);
        if(existing==null&&factor==1){message(s,actor,"Already at original size. No crystal used.");return;}
        float current=NativeGeometry.scale(s,target);var m=s.getComponent(target,ModelComponent.getComponentType()).getModel();
        if(existing==null&&Math.abs(current-m.getScale())>.001){message(s,actor,"Another system is controlling this entity's size. No crystal used.");return;}
        var fullBox=s.getComponent(target,BoundingBox.getComponentType()).getBoundingBox();
        if(existing==null&&(fullBox.width()>8||fullBox.height()>12||fullBox.depth()>8)){message(s,actor,"This entity is too large for the private ray. No crystal used.");return;}
        if(existing==null&&(current<.1||current>4)){message(s,actor,"This entity's baseline is outside the private prototype's safe range.");return;}
        var state=existing==null?new ShrinkState():existing;
        var pos=new Vector3d(s.getComponent(target,TransformComponent.getComponentType()).getPosition());
        if(existing==null){state.original=current;state.hadScale=s.getComponent(target,EntityScaleComponent.getComponentType())!=null;state.world=s.getExternalData().getWorld().getName();state.x=pos.x;state.y=pos.y;state.z=pos.z;}
        float desired=state.original*factor;
        if(emergency&&!NativeGeometry.clear(s,target,desired,pos)){
            var anchor=new Vector3d(state.x,state.y,state.z);
            if(!state.world.equals(s.getExternalData().getWorld().getName())||!NativeGeometry.clear(s,target,desired,anchor)||!NativeGeometry.solid(s.getExternalData().getWorld(),(int)Math.floor(anchor.x),(int)Math.floor(anchor.y-.08),(int)Math.floor(anchor.z))){message(s,actor,"Move into clear open space and use /shrinkium restore again. Your crystal is safe.");return;}
            var tp=Teleport.createForPlayer(anchor,s.getComponent(target,TransformComponent.getComponentType()).getRotation());
            var complete=new java.util.concurrent.CompletableFuture<Void>();tp.setOnComplete(complete);s.putComponent(target,Teleport.getComponentType(),tp);
            complete.whenComplete((v,error)->s.getExternalData().getWorld().execute(()->{if(error==null&&actor.isValid()&&actor.getStore()==s)fire(s,actor,true,true);}));return;
        }
        var inventory=s.getComponent(actor,Player.getComponentType()).getInventory().getCombinedHotbarFirst();
        ShrinkRules.Result result=ShrinkRules.activate(new ShrinkRules.Activation(){
            final CrystalCharge charge=new CrystalCharge(inventory);
            public boolean valid(){return eligible(s,target);}
            public boolean busy(){return state.busy();}
            public float current(){return current;}public float original(){return state.original;}
            public boolean clear(){return NativeGeometry.clear(s,target,desired,pos);}
            public boolean takeCrystal(){return charge.take();}
            public void refundCrystal(){charge.refund();}
            public void apply(float scale){var prior=existing==null?null:existing.clone();try{state.begin(current,scale);s.putComponent(target,stateType,state);ShrinkView.scale(s,target,current);}catch(RuntimeException e){if(prior==null)s.removeComponent(target,stateType);else s.putComponent(target,stateType,prior);throw e;}}
        },factor,emergency);
        if(result==ShrinkRules.Result.CHANGED){
            if(self)beam(s,NativeGeometry.eye(s,actor),new Vector3d(pos).add(0,.15,0),true);else beam(s,hit.start(),hit.end(),true);
            cue(s,factor==1?"Restore":"Fire",pos);message(s,actor,(emergency?"Free emergency self restoration":factor==1?"Restoring original size":"Target size: "+Math.round(factor*100)+"%")+(emergency?".":". One crystal used."));
            instance.getLogger().atInfo().log("SH_ACTIVATION factor=%s original=%s from=%s paid=%s self=%s",factor,state.original,current,!emergency,self);
        }else message(s,actor,switch(result){case BUSY->"Wait for the current transition. No crystal used.";case NO_OP->"Already at the selected size. No crystal used.";case OBSTRUCTED->"Not enough room to grow. Move into clear space. No crystal used.";case EMPTY->"Carry a Shrinkium crystal in your hotbar or main inventory.";default->"Invalid target. No crystal used.";});
    }
    final class Tick extends EntityTickingSystem<EntityStore>{
        @Override public Query<EntityStore>getQuery(){return Query.and(stateType,EntityScaleComponent.getComponentType(),ModelComponent.getComponentType(),BoundingBox.getComponentType(),TransformComponent.getComponentType());}
        @Override public void tick(float dt,int index,ArchetypeChunk<EntityStore>chunk,Store<EntityStore>s,CommandBuffer<EntityStore>buffer){
            var r=chunk.getReferenceTo(index);var state=chunk.getComponent(index,stateType);if(state.finishing)return;
            if(!Float.isFinite(state.original)||state.original<=0||!Float.isFinite(state.target)||state.target<=0)return;
            float current=NativeGeometry.scale(s,r);
            if(state.busy()){
                if(state.target>current&&!NativeGeometry.clear(s,r,state.target,s.getComponent(r,TransformComponent.getComponentType()).getPosition())){if(!state.blocked){state.blocked=true;message(s,r,"Growth paused: step clear, or /shrinkium restore for emergency recovery.");}ShrinkView.camera(s,r,state);return;}
                state.blocked=false;state.elapsed=Math.min(ShrinkRules.SECONDS,state.elapsed+Math.clamp(dt,0f,.1f));ShrinkView.scale(s,r,ShrinkRules.interpolate(state.from,state.target,state.elapsed));
            }
            ShrinkView.camera(s,r,state);
            if(!state.busy()&&Math.abs(state.target-state.original)<.0001f){state.finishing=true;s.getExternalData().getWorld().execute(()->{if(r.isValid()&&r.getStore()==s&&s.getComponent(r,stateType)==state){ShrinkView.scale(s,r,state.original);ShrinkView.reset(s,r,state);s.removeComponent(r,stateType);message(s,r,"Original size restored.");}});}
        }
    }
    final class Controls extends AbstractPlayerCommand{
        Controls(){super("shrinkium","Shrinkium controls; /shrinkium restore is free emergency self recovery");requireNoPermission();addSubCommand(new Restore());}
        @Override protected void execute(CommandContext c,Store<EntityStore>s,Ref<EntityStore>r,PlayerRef p,World w){RayPage.open(s,r);}
    }
    final class Restore extends AbstractPlayerCommand{
        Restore(){super("restore","Free emergency self restoration; no ray or crystal required");requireNoPermission();}
        @Override protected void execute(CommandContext c,Store<EntityStore>s,Ref<EntityStore>r,PlayerRef p,World w){fire(s,r,true,true);}
    }
}
