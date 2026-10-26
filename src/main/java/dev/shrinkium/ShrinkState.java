package dev.shrinkium;

import com.hypixel.hytale.codec.*;
import com.hypixel.hytale.codec.builder.BuilderCodec;
import com.hypixel.hytale.component.Component;
import com.hypixel.hytale.server.core.universe.world.storage.EntityStore;

/** Persist the original baseline and transition on the actual affected entity. */
public final class ShrinkState implements Component<EntityStore> {
    public static final BuilderCodec<ShrinkState> CODEC=BuilderCodec.builder(ShrinkState.class,ShrinkState::new)
        .append(new KeyedCodec<>("Original",Codec.FLOAT),(s,v)->s.original=v,s->s.original).add()
        .append(new KeyedCodec<>("From",Codec.FLOAT),(s,v)->s.from=v,s->s.from).add()
        .append(new KeyedCodec<>("Target",Codec.FLOAT),(s,v)->s.target=v,s->s.target).add()
        .append(new KeyedCodec<>("Elapsed",Codec.FLOAT),(s,v)->s.elapsed=v,s->s.elapsed).add()
        .append(new KeyedCodec<>("World",Codec.STRING),(s,v)->s.world=v,s->s.world).add()
        .append(new KeyedCodec<>("X",Codec.DOUBLE),(s,v)->s.x=v,s->s.x).add()
        .append(new KeyedCodec<>("Y",Codec.DOUBLE),(s,v)->s.y=v,s->s.y).add()
        .append(new KeyedCodec<>("Z",Codec.DOUBLE),(s,v)->s.z=v,s->s.z).add()
        .append(new KeyedCodec<>("OriginalHadScale",Codec.BOOLEAN),(s,v)->s.hadScale=v,s->s.hadScale).add().build();
    float original=1,from=1,target=1,elapsed=1; String world=""; double x,y,z; boolean hadScale;
    transient boolean finishing,blocked; transient float lastCamera=-1,lastSkinScale=-1;
    boolean busy(){return elapsed<ShrinkRules.SECONDS;}
    void begin(float current,float desired){from=current;target=desired;elapsed=0;blocked=false;finishing=false;}
    @Override public ShrinkState clone(){var s=new ShrinkState();s.original=original;s.from=from;s.target=target;s.elapsed=elapsed;s.world=world;s.x=x;s.y=y;s.z=z;s.hadScale=hadScale;return s;}
}
