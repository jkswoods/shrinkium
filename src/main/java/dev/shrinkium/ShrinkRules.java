package dev.shrinkium;

/** Small decision boundary shared by the runtime and adversarial quantity tests. */
final class ShrinkRules {
    static final float SECONDS=.85f;
    enum Result {CHANGED, INVALID, BUSY, NO_OP, OBSTRUCTED, EMPTY}
    interface Activation {
        boolean valid(); boolean busy(); boolean clear(); float current(); float original();
        boolean takeCrystal(); void apply(float target); void refundCrystal();
    }
    static boolean choice(float f){return f==.25f||f==.5f||f==.75f||f==1f;}
    static float interpolate(float from,float to,float elapsed){float t=Math.clamp(elapsed/SECONDS,0f,1f);return from+(to-from)*t*t*(3-2*t);}
    static Result activate(Activation a,float factor,boolean freeRecovery){
        if(!choice(factor)||!a.valid()||!Float.isFinite(a.original())||a.original()<=0||!Float.isFinite(a.current())||a.current()<=0)return Result.INVALID;
        if(a.busy()&&!freeRecovery)return Result.BUSY;
        float target=a.original()*factor;
        if(Math.abs(target-a.current())<.0001f&&!(freeRecovery&&a.busy()))return Result.NO_OP;
        if(target>a.current()&&!a.clear())return Result.OBSTRUCTED;
        if(!freeRecovery&&!a.takeCrystal())return Result.EMPTY;
        try{a.apply(target);}catch(RuntimeException e){if(!freeRecovery)a.refundCrystal();throw e;}
        return Result.CHANGED;
    }
    /** Ray/AABB first intersection; positive infinity means no hit. */
    static double intersect(double[] origin,double[] direction,double[] min,double[] max,double limit){
        double near=0,far=limit;
        for(int i=0;i<3;i++){
            if(Math.abs(direction[i])<1e-10){if(origin[i]<min[i]||origin[i]>max[i])return Double.POSITIVE_INFINITY;continue;}
            double a=(min[i]-origin[i])/direction[i],b=(max[i]-origin[i])/direction[i];
            near=Math.max(near,Math.min(a,b));far=Math.min(far,Math.max(a,b));if(far<near)return Double.POSITIVE_INFINITY;
        }return near;
    }
}
