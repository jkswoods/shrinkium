package dev.shrinkium;
import com.hypixel.hytale.component.*;
import com.hypixel.hytale.protocol.BlockMaterial;
import com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType;
import com.hypixel.hytale.server.core.modules.entity.component.*;
import com.hypixel.hytale.server.core.universe.world.World;
import com.hypixel.hytale.server.core.universe.world.chunk.section.BlockSection;
import com.hypixel.hytale.server.core.universe.world.storage.EntityStore;
import com.hypixel.hytale.math.shape.Box;
import org.joml.Vector3d;

final class NativeGeometry {
    static final double RANGE=16;
    static float scale(Store<EntityStore>s,Ref<EntityStore>r){var c=s.getComponent(r,EntityScaleComponent.getComponentType());return c==null?s.getComponent(r,ModelComponent.getComponentType()).getModel().getScale():c.getScale();}
    static Vector3d eye(Store<EntityStore>s,Ref<EntityStore>r){var m=s.getComponent(r,ModelComponent.getComponentType()).getModel();return new Vector3d(s.getComponent(r,TransformComponent.getComponentType()).getPosition()).add(0,ModelComponent.getEyeHeight(r,s)*scale(s,r)/m.getScale(),0);}
    static boolean solid(World w,int x,int y,int z){var cs=w.getChunkStore();var r=cs.getChunkSectionReferenceAtBlock(x,y,z);if(r==null||!r.isValid())return true;var b=cs.getStore().getComponent(r,BlockSection.getComponentType());if(b==null)return true;int id=b.get(x&31,y&31,z&31);var type=BlockType.getAssetMap().getAsset(id);return type==null||type.getMaterial()==BlockMaterial.Solid||b.getFiller(x&31,y&31,z&31)!=0;}
    static double wall(World w,Vector3d at,Vector3d dir){for(double t=0;t<=RANGE;t+=.05){var p=new Vector3d(at).fma(t,dir);if(solid(w,(int)Math.floor(p.x),(int)Math.floor(p.y),(int)Math.floor(p.z)))return t;}return RANGE;}
    static Box box(Store<EntityStore>s,Ref<EntityStore>r,float target){var b=s.getComponent(r,BoundingBox.getComponentType()).getBoundingBox();return new Box(b).scale(target/scale(s,r));}
    static boolean clear(Store<EntityStore>s,Ref<EntityStore>r,float target,Vector3d pos){
        var b=box(s,r,target);if(b.width()>8||b.height()>12||b.depth()>8)return false;var w=s.getExternalData().getWorld();
        for(int x=(int)Math.floor(pos.x+b.min.x+.01);x<=Math.floor(pos.x+b.max.x-.01);x++)for(int y=(int)Math.floor(pos.y+b.min.y+.02);y<=Math.floor(pos.y+b.max.y-.01);y++)for(int z=(int)Math.floor(pos.z+b.min.z+.01);z<=Math.floor(pos.z+b.max.z-.01);z++)if(solid(w,x,y,z))return false;
        return true;
    }
    record Hit(Ref<EntityStore>target,Vector3d start,Vector3d end){}
    static Hit aim(Store<EntityStore>s,Ref<EntityStore>r){
        var start=eye(s,r);var h=s.getComponent(r,HeadRotation.getComponentType());if(h==null)return new Hit(null,start,start);var dir=new Vector3d(h.getDirection()).normalize();double stop=wall(s.getExternalData().getWorld(),start,dir),best=stop;Ref<EntityStore> chosen=null;
        for(var other:com.hypixel.hytale.server.core.util.TargetUtil.getAllEntitiesInSphere(start,RANGE+4,s)){
            if(other.equals(r)||!ShrinkiumPlugin.eligible(s,other))continue;
            var pos=s.getComponent(other,TransformComponent.getComponentType()).getPosition();var box=s.getComponent(other,BoundingBox.getComponentType()).getBoundingBox();
            double t=ShrinkRules.intersect(new double[]{start.x,start.y,start.z},new double[]{dir.x,dir.y,dir.z},new double[]{pos.x+box.min.x,pos.y+box.min.y,pos.z+box.min.z},new double[]{pos.x+box.max.x,pos.y+box.max.y,pos.z+box.max.z},stop);
            if(t<best){best=t;chosen=other;}
        }return new Hit(chosen,start,new Vector3d(start).fma(best,dir));
    }
}
