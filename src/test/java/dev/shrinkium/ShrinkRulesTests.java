package dev.shrinkium;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
final class ShrinkRulesTests {
    static int checks;
    static void check(boolean condition,String message){checks++;if(!condition)throw new AssertionError(message);}
    static final class Fixture implements ShrinkRules.Activation {
        int crystals=3,changes;float size=1,original=1;boolean valid=true,busy,clear=true,fail;
        public boolean valid(){return valid;}public boolean busy(){return busy;}public boolean clear(){return clear;}public float current(){return size;}public float original(){return original;}
        public boolean takeCrystal(){if(crystals==0)return false;crystals--;return true;}public void refundCrystal(){crystals++;}
        public void apply(float target){if(fail)throw new IllegalStateException("injected mutation failure");size=target;changes++;busy=true;}
    }
    public static void main(String[]args)throws Exception{
        for(float factor:new float[]{.25f,.5f,.75f}){var f=new Fixture();check(ShrinkRules.activate(f,factor,false)==ShrinkRules.Result.CHANGED,"size choice");check(f.crystals==2&&f.size==factor,"one crystal independent of amount");check(ShrinkRules.activate(f,factor,false)==ShrinkRules.Result.BUSY,"double activation busy");check(f.crystals==2,"busy does not charge");f.busy=false;check(ShrinkRules.activate(f,factor,false)==ShrinkRules.Result.NO_OP&&f.crystals==2,"no op");check(ShrinkRules.activate(f,1,false)==ShrinkRules.Result.CHANGED&&f.crystals==1&&f.size==1,"paid restore");}
        for(int i=0;i<5;i++){var f=new Fixture();if(i==0)f.valid=false;if(i==1)f.original=Float.NaN;if(i==2)f.size=Float.NaN;if(i==3)f.original=0;float choice=i==4?.1f:.5f;check(ShrinkRules.activate(f,choice,false)==ShrinkRules.Result.INVALID&&f.crystals==3&&f.changes==0,"invalid refuses free");}
        var empty=new Fixture();empty.crystals=0;check(ShrinkRules.activate(empty,.5f,false)==ShrinkRules.Result.EMPTY&&empty.changes==0,"empty crystal refuses mutation");
        var grow=new Fixture();grow.size=.25f;grow.clear=false;check(ShrinkRules.activate(grow,1,false)==ShrinkRules.Result.OBSTRUCTED&&grow.crystals==3,"no paid blocked growth");check(ShrinkRules.activate(grow,1,true)==ShrinkRules.Result.OBSTRUCTED,"free recovery also checks clearance");grow.clear=true;grow.crystals=0;grow.busy=true;check(ShrinkRules.activate(grow,1,true)==ShrinkRules.Result.CHANGED&&grow.size==1&&grow.crystals==0,"free recovery cancels transition");
        var failing=new Fixture();failing.fail=true;try{ShrinkRules.activate(failing,.5f,false);throw new AssertionError("failure not propagated");}catch(IllegalStateException expected){}check(failing.crystals==3&&failing.changes==0,"mutation failure refunds exact charge");
        var concurrent=new Fixture();var executor=Executors.newSingleThreadExecutor();var requests=new java.util.ArrayList<Future<?>>();var changed=new AtomicInteger();for(int i=0;i<100;i++)requests.add(executor.submit(()->{if(ShrinkRules.activate(concurrent,.25f,false)==ShrinkRules.Result.CHANGED)changed.incrementAndGet();}));for(var r:requests)r.get();executor.shutdown();check(changed.get()==1&&concurrent.crystals==2&&concurrent.changes==1,"world-serialized100 activations exactly one charge/change");
        var baseline=new Fixture();baseline.original=.8f;baseline.size=.8f;ShrinkRules.activate(baseline,.25f,false);baseline.busy=false;check(Math.abs(baseline.size-.2f)<.0001,"relative to captured native baseline");ShrinkRules.activate(baseline,.5f,false);check(Math.abs(baseline.size-.4f)<.0001,"absolute factors do not stack");
        float prior=1;for(int i=0;i<=85;i++){float f=ShrinkRules.interpolate(1,.25f,i*.01f);check(f<=prior+.00001&&f>=.25f&&f<=1,"monotonic bounded transition");prior=f;}check(ShrinkRules.interpolate(1,.25f,10)==.25f,"oversized frame clamps");
        check(ShrinkRules.intersect(new double[]{0,1,0},new double[]{0,0,1},new double[]{-.2,.5,5},new double[]{.2,1.5,6},16)==5,"first AABB surface");check(Double.isInfinite(ShrinkRules.intersect(new double[]{1,1,0},new double[]{0,0,1},new double[]{-.2,.5,5},new double[]{.2,1.5,6},16)),"off-axis miss");check(Double.isInfinite(ShrinkRules.intersect(new double[]{0,1,0},new double[]{0,0,1},new double[]{-.2,.5,5},new double[]{.2,1.5,6},4)),"wall occlusion limit");
        var cancel=new Fixture();cancel.busy=true;cancel.size=1;check(ShrinkRules.activate(cancel,1,true)==ShrinkRules.Result.CHANGED&&! (cancel.size!=1),"emergency cancels just-started shrink before first tick");
        System.out.println("SH_RULES_PASS checks="+checks);
    }
}
