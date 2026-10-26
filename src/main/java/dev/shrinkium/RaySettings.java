package dev.shrinkium;
import com.hypixel.hytale.codec.*;
import com.hypixel.hytale.codec.builder.BuilderCodec;
import com.hypixel.hytale.component.Component;
import com.hypixel.hytale.server.core.universe.world.storage.EntityStore;
public final class RaySettings implements Component<EntityStore> {
    public static final BuilderCodec<RaySettings> CODEC=BuilderCodec.builder(RaySettings.class,RaySettings::new)
        .append(new KeyedCodec<>("Factor",Codec.FLOAT),(s,v)->s.factor=v,s->s.factor).add().build();
    float factor=.5f; transient long nextShot;
    @Override public RaySettings clone(){var s=new RaySettings();s.factor=factor;return s;}
}
