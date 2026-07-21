	Program transform
c
c	Transformation des fichiers data rh‚ologiques en fichiers
c	d'entr‚e pour CONTIN
c
c	modifi‚ le 7/11/95
c
	Character	fich*14,li*50,gm*8,lj*50,lk*80
	Dimension	t(256),y(256)
c
	open (unit=9,file=' ',access='sequential',form='formatted')
	inquire (unit=9, name=fich)
	fich(10:13) = '.dat'
	open (unit=8,file=fich,access='sequential',form='formatted')
	write	(9,100)fich(1:8)
	write	(9,100)' IFORMY    0    .00'
	write	(9,100)' (6E13.7)'
	write	(9,100)' IFORMT    0    .00'
	write	(9,100)' (6E13.7)'
	write	(9,100)' IFORMW    0    .00'
	write	(9,100)' (6E13.7)'
	write	(9,100)' NINTT     0   -1.00'
	write	(9,100)' DOUSNQ    0    1.00'
	write	(9,100)' IQUAD          1.00'
	write	(9,100)' PRWT      0   -1.00'
	write	(9,100)' PRY       0   -1.00'
	write	(9,100)' IPLRES    1    2.00'
	write	(9,100)' IPLRES    2    2.00'
	write	(9,100)' IPRINT    1    0.00'
	write	(9,100)' IPRINT    2    2.00'
	write	(9,100)' IPLFIT    1    0.00'
	write	(9,100)' IPLFIT    2    0.00'
	write	(9,100)' NONNEG    1    1.00'
	write	(9,100)' IWT       0    5.00'
	write	(9,100)' NQPROG    1    5.00'
	write	(9,100)' NQPROG    2    5.00'
c
c
	do 1 i=1,3
 	read	(8,100)li
 1	li(1:50)=' '
	li(1:16)=' GMNMX     1  '
	write	(5,212)
	read	(5,150)b1
	write	(5,213)
	read	(5,150)b2
 150	format(e12.5)
	write (li(17:24),151)b1
	write	(9,100)li
	li(1:16)=' GMNMX     2   '
	write (li(17:24),151)b2
	write	(9,100)li
 151	format(e8.3)
c
	write	(9,100)' RUSER    10    .00'
	write	(9,100)' NG        0    40.00'
	write	(9,100)' NLINF     0    1.00'
	write	(9,100)' IUSER    10    4.00'
	write	(9,100)' RUSER    21    1.0'
	write	(9,100)' RUSER    22   -1.0'
	write	(9,100)' RUSER    23    0.0'
 	read	(8,100)li
	li(1:16)=' RUSER    18'
	write	(9,100)li
	read	(8,100)li
	li(1:16)=' RUSER    17'
	li(25:25)='.'
	write	(9,100)li
	read	(8,100)li
	li(1:16)=' RUSER    19'
	li(25:25)='.'
	write	(9,100)li
	read	(8,100)li
	li(1:16)=' RUSER    15'
	write	(9,100)li
	read	(8,100)li
	li(1:16)=' RUSER    16'
	li(25:25)='.'
	write	(9,100)li
	read	(8,100)li
	write	(9,100)' END       0    0.00'
	read	(8,100)li
	lj(1:50)=' '
	lj(1:3)=' NY'
	read	(li(5:7),113)ny
	write	(lj(10:12),118)ny
	write	(9,100)lj
c
c	initialize variables t(i) and y(i) :
c
	do 17 i=1,256
 	y(i)=0.
	t(i)=0.
 17	continue
c
c	read t(i) and y(i) :
c
	do 15 i=1,ny
	read	(8,*) t(i), y(i)
 15	continue
c
c	write data t(i) and y(i) :
c
	write	(9,115)(t(i),i=1,ny)
	write	(9,117)(y(i),i=1,ny)
c
	close (8)
	close (9)
c
c	used formats :
c
 100	format(50a)
 111	format(a14)
 112	format(a8)
 113	format(i5)
 115	format(6e13.7)
 116	format(3e13.7)
 117	format(6e13.7)
 118	format(i3)
 120	format(80a)
 121	format(f12.7)
 122	format(4e15.7)
c
 211	format(' nom de fichier ? '$)
 212	format(1x,'TMIN(seconde) ? '$)
 213	format(1x,'TMAX(seconde) ? '$)
	end
