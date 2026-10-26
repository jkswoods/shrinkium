package dev.shrinkium;
import com.hypixel.hytale.server.core.asset.type.blocktype.config.BlockType;
import com.hypixel.hytale.server.core.universe.world.events.ChunkPreLoadProcessEvent;
import com.hypixel.hytale.server.core.universe.world.chunk.ChunkColumn;
import com.hypixel.hytale.server.core.universe.world.chunk.section.*;
import com.hypixel.hytale.server.core.universe.world.chunk.heightmap.*;
import java.util.Random;
/** Decorate only first-generation native home terrain; no retroactive save edits. */
final class CrystalFeatures {
    static void column(ChunkPreLoadProcessEvent e){
        if(!e.isNewlyGenerated()||!e.getWorld().getName().equals("default"))return;
        var column=e.getHolder().getComponent(ChunkColumn.getComponentType());if(column==null||column.getSectionHolders()==null)return;
        var heights=new HeightmapColumn(new LegacyHeightmap());
        for(var h:column.getSectionHolders())if(h!=null){var at=h.getComponent(ChunkSection.getComponentType());var b=h.getComponent(BlockSection.getComponentType());if(at!=null&&b!=null)heights.onSectionGenerated(at.getY(),b);}
        var map=BlockType.getAssetMap();int ore=map.getIndex("SH_Ore_Stone");if(ore==Integer.MIN_VALUE)return;
        for(var h:column.getSectionHolders())if(h!=null){var at=h.getComponent(ChunkSection.getComponentType());var b=h.getComponent(BlockSection.getComponentType());if(at==null||b==null)continue;
            decorate(b,heights,e.getWorld().getWorldConfig().getSeed(),at.getX(),at.getY(),at.getZ());
        }
    }
    static int decorate(BlockSection b,HeightmapColumn heights,long seed,int cx,int sy,int cz){
        var map=BlockType.getAssetMap();int ore=map.getIndex("SH_Ore_Stone");if(ore==Integer.MIN_VALUE)return 0;
            var rng=new Random(seed^((long)cx*0x632be59bd9b4e019L)^((long)sy*0x94d049bb133111ebL)^((long)cz*0x9e3779b9L)^0x534852494e4bL);
            int placed=0;for(int i=0;i<500&&placed<2;i++){
                int x=1+rng.nextInt(30),y=1+rng.nextInt(30),z=1+rng.nextInt(30);int top=heights.getHeight(x,z);if(top==HeightmapColumn.NO_HEIGHT||top-(sy*32+y)<24)continue;
                var host=map.getAsset(b.get(x,y,z));if(host==null||!host.getId().equals("Rock_Stone"))continue;
                boolean cave=b.get(x+1,y,z)==BlockType.EMPTY_ID||b.get(x-1,y,z)==BlockType.EMPTY_ID||b.get(x,y+1,z)==BlockType.EMPTY_ID||b.get(x,y-1,z)==BlockType.EMPTY_ID||b.get(x,y,z+1)==BlockType.EMPTY_ID||b.get(x,y,z-1)==BlockType.EMPTY_ID;
                if(cave){b.set(x,y,z,ore,0,0);placed++;}
            }
        return placed;
    }
}
