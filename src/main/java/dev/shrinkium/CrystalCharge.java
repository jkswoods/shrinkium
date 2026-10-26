package dev.shrinkium;
import com.hypixel.hytale.server.core.inventory.ItemStack;
import com.hypixel.hytale.server.core.inventory.container.ItemContainer;
/** One native compare-and-replace; metadata and other stacks remain intact. World-thread only. */
final class CrystalCharge {
    final ItemContainer inventory; ItemStack before,after;short slot=-1;boolean paid;
    CrystalCharge(ItemContainer inventory){this.inventory=inventory;}
    boolean take(){
        if(paid)return false;
        for(short i=0;i<inventory.getCapacity();i++){
            var stack=inventory.getItemStack(i);
            if(stack!=null&&"SH_Crystal".equals(stack.getItemId())&&stack.getQuantity()>0){before=stack;after=stack.getQuantity()==1?ItemStack.EMPTY:stack.withQuantity(stack.getQuantity()-1);slot=i;paid=inventory.replaceItemStackInSlot(i,before,after).succeeded();if(paid)after=inventory.getItemStack(i);return paid;}
        }return false;
    }
    void refund(){if(!paid)return;if(!inventory.replaceItemStackInSlot(slot,after,before).succeeded())throw new IllegalStateException("Crystal rollback refused; retained original slot "+slot);paid=false;}
}
