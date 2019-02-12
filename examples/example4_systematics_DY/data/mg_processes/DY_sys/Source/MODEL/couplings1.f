ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
c      written by the UFO converter
ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc

      SUBROUTINE COUP1()

      IMPLICIT NONE
      INCLUDE 'model_functions.inc'

      DOUBLE PRECISION PI, ZERO
      PARAMETER  (PI=3.141592653589793D0)
      PARAMETER  (ZERO=0D0)
      INCLUDE 'input.inc'
      INCLUDE 'coupl.inc'
      GC_2 = (2.000000D+00*MDL_EE*MDL_COMPLEXI)/3.000000D+00
      GC_3 = -(MDL_EE*MDL_COMPLEXI)
      GC_27 = -(MDL_CW*MDL_EE*MDL_COMPLEXI)/(2.000000D+00*MDL_SW)
      GC_28 = (MDL_CW*MDL_EE*MDL_COMPLEXI)/(2.000000D+00*MDL_SW)
      GC_35 = -(MDL_EE*MDL_COMPLEXI*MDL_SW)/(6.000000D+00*MDL_CW)
      GC_36 = (MDL_EE*MDL_COMPLEXI*MDL_SW)/(2.000000D+00*MDL_CW)
      GC_46 = (MDL_CWHAT*MDL_COMPLEXI)/MDL_VEV__EXP__2+(MDL_CYHAT
     $ *MDL_COMPLEXI*MDL_SW__EXP__2)/(3.000000D+00*MDL_CW__EXP__2
     $ *MDL_VEV__EXP__2)
      GC_54 = (2.000000D+00*MDL_CYHAT*MDL_COMPLEXI*MDL_SW__EXP__2)
     $ /(3.000000D+00*MDL_CW__EXP__2*MDL_VEV__EXP__2)
      GC_58 = (4.000000D+00*MDL_CYHAT*MDL_COMPLEXI*MDL_SW__EXP__2)
     $ /(3.000000D+00*MDL_CW__EXP__2*MDL_VEV__EXP__2)
      GC_61 = (8.000000D+00*MDL_CYHAT*MDL_COMPLEXI*MDL_SW__EXP__2)
     $ /(3.000000D+00*MDL_CW__EXP__2*MDL_VEV__EXP__2)
      END
