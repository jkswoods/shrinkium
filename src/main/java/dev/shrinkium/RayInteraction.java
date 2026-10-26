package dev.shrinkium;
import com.hypixel.hytale.codec.builder.BuilderCodec;
import com.hypixel.hytale.protocol.InteractionType;
import com.hypixel.hytale.server.core.entity.InteractionContext;
import com.hypixel.hytale.server.core.modules.interaction.interaction.CooldownHandler;
import com.hypixel.hytale.server.core.modules.interaction.interaction.config.SimpleInstantInteraction;
public final class RayInteraction extends SimpleInstantInteraction {
    public static final BuilderCodec<RayInteraction> CODEC=BuilderCodec.builder(RayInteraction.class,RayInteraction::new,SimpleInstantInteraction.CODEC).build();
    @Override protected void firstRun(InteractionType type,InteractionContext context,CooldownHandler cooldown){
        var buffer=context.getCommandBuffer();var r=context.getEntity();var held=context.getHeldItem();var container=context.getHeldItemContainer();short slot=context.getHeldItemSlot();
        if(held==null||container==null||!"SH_Ray".equals(held.getItemId()))return;
        buffer.getExternalData().getWorld().execute(()->{if(r.isValid()&&held.equals(container.getItemStack(slot))){if(type==InteractionType.Secondary)RayPage.open(r.getStore(),r);else if(type==InteractionType.Primary)ShrinkiumPlugin.fire(r.getStore(),r,false,false);}});
    }
}
