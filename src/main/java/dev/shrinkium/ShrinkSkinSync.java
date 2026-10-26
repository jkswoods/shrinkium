package dev.shrinkium;
import com.hypixel.hytale.component.*;
import com.hypixel.hytale.component.dependency.*;
import com.hypixel.hytale.component.query.Query;
import com.hypixel.hytale.component.system.tick.EntityTickingSystem;
import com.hypixel.hytale.server.core.modules.entity.player.PlayerSkinComponent;
import com.hypixel.hytale.server.core.modules.entity.component.EntityScaleComponent;
import com.hypixel.hytale.server.core.modules.entity.tracker.EntityTrackerSystems;
import com.hypixel.hytale.server.core.universe.PlayerRef;
import com.hypixel.hytale.server.core.universe.world.storage.EntityStore;
import java.util.Set;
/** Resend retained skin after changed scale, avoiding repeated invalidation of settled render state. */
final class ShrinkSkinSync extends EntityTickingSystem<EntityStore>{
 @Override public Query<EntityStore>getQuery(){return Query.and(ShrinkiumPlugin.stateType,PlayerRef.getComponentType(),PlayerSkinComponent.getComponentType(),EntityScaleComponent.getComponentType());}
 @Override public SystemGroup<EntityStore>getGroup(){return EntityTrackerSystems.QUEUE_UPDATE_GROUP;}
 @Override public Set<Dependency<EntityStore>>getDependencies(){return Set.of(new SystemDependency<>(Order.AFTER,EntityTrackerSystems.EntityModel.class),new SystemDependency<>(Order.BEFORE,EntityTrackerSystems.EntitySkin.class));}
 @Override public void tick(float dt,int index,ArchetypeChunk<EntityStore>chunk,Store<EntityStore>s,CommandBuffer<EntityStore>b){var r=chunk.getReferenceTo(index);var state=chunk.getComponent(index,ShrinkiumPlugin.stateType);float scale=NativeGeometry.scale(s,r);if(Math.abs(scale-state.lastSkinScale)>.00001f){state.lastSkinScale=scale;chunk.getComponent(index,PlayerSkinComponent.getComponentType()).setNetworkOutdated();}}
}
