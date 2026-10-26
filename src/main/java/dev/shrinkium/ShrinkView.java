package dev.shrinkium;
import com.hypixel.hytale.component.*;
import com.hypixel.hytale.protocol.*;
import com.hypixel.hytale.protocol.packets.camera.SetServerCamera;
import com.hypixel.hytale.server.core.modules.entity.component.*;
import com.hypixel.hytale.server.core.modules.entity.player.PlayerSkinComponent;
import com.hypixel.hytale.server.core.universe.PlayerRef;
import com.hypixel.hytale.server.core.universe.world.storage.EntityStore;
final class ShrinkView {
    static void scale(Store<EntityStore>s,Ref<EntityStore>r,float size){var c=s.getComponent(r,EntityScaleComponent.getComponentType());if(c==null)s.putComponent(r,EntityScaleComponent.getComponentType(),new EntityScaleComponent(size));else c.setScale(size);var m=s.getComponent(r,ModelComponent.getComponentType());s.getComponent(r,BoundingBox.getComponentType()).setScale(size/m.getModel().getScale());}
    static void camera(Store<EntityStore>s,Ref<EntityStore>r,ShrinkState state){
        var p=s.getComponent(r,PlayerRef.getComponentType());if(p==null)return;float height=(float)(NativeGeometry.eye(s,r).y-s.getComponent(r,TransformComponent.getComponentType()).getPosition().y);
        if(Math.abs(height-state.lastCamera)<.005f)return;state.lastCamera=height;
        var c=new ServerCameraSettings();c.isFirstPerson=true;c.hideHeldItem=false;c.eyeOffset=false;c.allowPitchControls=true;c.displayReticle=true;c.distance=0;c.skipCharacterPhysics=false;
        c.attachedToType=AttachedToType.LocalPlayer;c.followAttachedEntity=true;c.positionType=PositionType.AttachedToPlusOffset;c.positionOffset=new Position(0,height,0);c.rotationType=RotationType.AttachedToPlusOffset;c.rotationOffset=new Direction(0,0,0);c.applyLookType=ApplyLookType.LocalPlayerLookOrientation;c.applyMovementType=ApplyMovementType.CharacterController;c.canMoveType=CanMoveType.Always;c.positionLerpSpeed=1;c.rotationLerpSpeed=1;
        p.getPacketHandler().writeNoCache(new SetServerCamera(ClientCameraView.Custom,true,c));
    }
    static void reset(Store<EntityStore>s,Ref<EntityStore>r,ShrinkState state){
        if(!state.hadScale)s.removeComponent(r,EntityScaleComponent.getComponentType());
        var skin=s.getComponent(r,PlayerSkinComponent.getComponentType());if(skin!=null)skin.setNetworkOutdated();
        var p=s.getComponent(r,PlayerRef.getComponentType());if(p!=null)p.getPacketHandler().writeNoCache(new SetServerCamera(ClientCameraView.Custom,false,null));
    }
}
