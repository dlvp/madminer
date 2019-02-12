
C     PY ((2, -2), (-13, 13)) : (2, -2, -13, 13) # M0_
      SUBROUTINE SMATRIXHEL(PDGS, NPDG, P, ALPHAS, SCALE2, NHEL, ANS)
      IMPLICIT NONE

CF2PY double precision, intent(in), dimension(0:3,npdg) :: p
CF2PY integer, intent(in), dimension(npdg) :: pdgs
CF2PY integer, intent(in) :: npdg
CF2PY double precision, intent(out) :: ANS
CF2PY double precision, intent(in) :: ALPHAS
CF2PY double precision, intent(in) :: SCALE2
      INTEGER PDGS(*)
      INTEGER NPDG, NHEL
      DOUBLE PRECISION P(*)
      DOUBLE PRECISION ANS, ALPHAS, PI,SCALE2
      INCLUDE 'coupl.inc'

      PI = 3.141592653589793D0
      G = 2* DSQRT(ALPHAS*PI)
      CALL UPDATE_AS_PARAM()
      IF (SCALE2.NE.0D0) STOP 1

      IF(2.EQ.PDGS(1).AND.-2.EQ.PDGS(2).AND.-13.EQ.PDGS(3)
     $ .AND.13.EQ.PDGS(4)) THEN  ! 3
        CALL M0_SMATRIXHEL(P, NHEL, ANS)
      ENDIF

      RETURN
      END

      SUBROUTINE INITIALISE(PATH)
C     ROUTINE FOR F2PY to read the benchmark point.
      IMPLICIT NONE
      CHARACTER*512 PATH
CF2PY INTENT(IN) :: PATH
      CALL SETPARA(PATH)  !first call to setup the paramaters
      RETURN
      END

      SUBROUTINE GET_PDG_ORDER(PDG)
      IMPLICIT NONE
CF2PY INTEGER, intent(out) :: PDG(1,4)
      INTEGER PDG(1,4), PDGS(1,4)
      DATA PDGS/ 2,-2,-13,13 /
      PDG = PDGS
      RETURN
      END

      SUBROUTINE GET_PREFIX(PREFIX)
      IMPLICIT NONE
CF2PY CHARACTER*20, intent(out) :: PREFIX(1)
      CHARACTER*20 PREFIX(1),PREF(1)
      DATA PREF / 'M0_'/
      PREFIX = PREF
      RETURN
      END



