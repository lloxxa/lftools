def merge_two_dicts(x, y): # move to lftools
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

path_to_MB='/Users/aljosha/stack/PCC-PhD/Data/Rheology/MB-301/intervals/'
MBpaths={	'A01-Zn-C01':'/Users/aljosha/stack/PCC-PhD/Data/Rheology/MB-301/intervals/20170516-MB20-Rheo_A01-Zn-C01_100%-cone-coverage-1/',
	'A0-Zn-C0-1':'20170419-MB17-A0C0Zn-seriesNo2-1',
	'A0-Zn-C0-2':'20170419-MB17-A0C0Zn-seriesNo2-2',
	'A0-Zn-C0-3':'20170419-MB17-A0C0Zn-seriesNo2-3',
	'A0-Zn-C0-break-1':'20170419-MB17-A0C0Zn-seriesNo2-break-it-1',
	'A0-Zn-C0-break-2':'20170419-MB17-A0C0Zn-seriesNo2-break-it-2',
	'A0-Zn-C0-break-3':'20170419-MB17-A0C0Zn-seriesNo2-break-it-3',
	'A0-Ni-C0-1':'20170420-MB17-A0NiC0-1',   
	'A0-Ni-C0-2':'20170420-MB17-A0NiC0-2',
	'A0-Ni-C0-3':'20170420-MB17-A0NiC0-3',
	'A0-Ni-C0-4':'20170420-MB17-A0NiC0-4', # empty ampswp
	'A0-Ni-C0-reload-1':'20170420-MB17-A0NiC0-after-lift-up-and-lower-cone-once-again-1',
	'A0-Ni-C0-reload-2':'20170420-MB17-A0NiC0-after-lift-up-and-lower-cone-once-again-2',
	'A0-10xZn-C01-1':'20170424-MB17-A0-10xZn-C01-1',
	'A0-10xZn-C01-2':'20170424-MB17-A0-10xZn-C01-2',
	'A0-10xZn-C01-3':'20170424-MB17-A0-10xZn-C01-3',
	'A0-Zn-C01-1':'20170424-MB17-A0-1xZn-C01-1',
	'A0-Zn-C01-2':'20170424-MB17-A0-1xZn-C01-2',
	'A0-C01-1':'20170425-MB17-A0-C01-1',
	'A0-Ni-C01-1':'20170426-MB17-A0-Ni-C01-1', # probably not covered or at measurement gap
	'A0-Ni-C01-10':'20170426-MB17-A0-Ni-C01-10', # probably not covered or at measurement gap
	'A0-Ni-C01-5':'20170426-MB17-A0-Ni-C01-5',
	'A0-Ni-C01-8':'20170426-MB17-A0-Ni-C01-8',
	'C01-Zn-A0-1':'20170428-MB17_C01-ZnA0-1',
	'C01-Zn-A0-2':'20170428-MB17_C01-ZnA0-2',
	'C01-Zn-A0-break-1':'20170428-MB17_C01-ZnA0_break-it-1',
	'C01-Zn-A0-break-2':'20170428-MB17_C01-ZnA0_break-it-2',
	'A0-C0-1':'20170501-MB17-Rheology_A0-C0-1',
	'A0-C0-break-1':'20170501-MB17-Rheology_A0-C0-breakit-1',
	'A01-Zn-C0-1':'20170501-MB17_A01-ZnC0-1',
	'A01-Zn-C0-break-1':'20170501-MB17_A01-ZnC0-break-it-1',
	'A01-Zn-C0-break-2':'20170501-MB17_A01-ZnC0-break-it-2',
	'A01-Zn-C0-frqswp-1':'20170501-MB17_A01-ZnC0-more-freq-sweeps-1',
	'A01-Zn-C0-frqswp-2':'20170501-MB17_A01-ZnC0-more-freq-sweeps-2',
	'A0-Zn10pct-C0-0.9cc-1':'20170502-MB17-Rheology_A0-Znfor10%-C0-90%-cone-coverage-1',
	'A0-Zn10pct-C0-0.9cc-2':'20170502-MB17-Rheology_A0-Znfor10%-C0-90%-cone-coverage-2',
	'A0-Mn-C10-1M-NaCl':'20170509-MB17-Rheology_A0-Mn-C10-1M-NaCl-5-ml-total-sample-volume-1',	#
	'A01-C0-0.83M-NaCl':'20170510-MB20-Rheo-0.83Msalt_A01-C0-1', 					#
	'A01-Mn-C0-0.83M-NaCl':'20170510-MB20-Rheo-0.83Msalt_A01-Mn-C0-1',				#
	'A01-Ni-C01-3':'20170515-MB20-Rheo_A01-Ni-C01_100-percent-cone-coverage-3',			#
	'A01-Mn-C01-1':'20170515_MB20-Rheo_A01-Mn-C01_no-cone-coverage-check-1',			# messed up relaxation curve
	'A01-Zn-C01-1':'20170516-MB20-Rheo_A01-Zn-C01_100%-cone-coverage-1',
	'A0-Ni-C10-1':'20170516_MB20_Rheo_A0-Ni-C10_100%-cone-coverage-1',				#
	'A0-Ni-C01-1':'20170517-MB20-Rheo_A0-Ni-C01_100%-cone-coverage-1',				# only frqswp
	'A0-Ni-C01-2':'20170517-MB20-Rheo_A0-Ni-C01_100%-cone-coverage-2',				# only frqswp
	'A0-Zn-C0':'20170518-MB17-Rheology_A0-Zn-C0-1',							# only frqswp
	'A0-Zn-C0-0.9cc':'20170518-MB17-Rheology_A0-Zn-C0_90%-cone-coverage-1',				# complete set
	'A10-Zn-C0-0.9cc':'20170518-MB20-Rheology_A10-C0_90%-cone-coverage-1',				# complete set
	'A10-Zn-C0-0.8cc':'20170518-MB20-Rheology_A10-ZnC0_80%-cone-coverage-1',			# complete set
	'A0-Mn-C10-0.1M-NaCl-0.9cc-1':'20170519--MB17-Rheology_A0-Mn-C10_1e-1M-NaCl_3mlNacl-firstorder_90%-cov-1', # complete set
	'A0-Mn-C10-0.1M-NaCl-0.9cc-2':'20170519--MB17-Rheology_A0-Mn-C10_1e-1M-NaCl_3mlNacl-firstorder_90%-cov-2', # complete set
	'A0-Mn-C10-0.1M-NaCl-0.9cc-3':'20170519--MB17-Rheology_A0-Mn-C10_1e-1M-NaCl_3mlNacl-firstorder_90%-cov-3', # breaking it
	'A0-C10-0.5M-NaCl':'20170519-MB17-Rheology_A0-C10_5e-1MNaCl_100%-cone-coverage-1',		#
	'A0-Mn-C0-0.1M-NaCl-1':'20170519-MB17-Rheology_A0-Mn-C0_1e-1M-NaCl_100%-cone-coverage-1',	#
	'A0-Mn-C0-0.1M-NaCl-2':'20170519-MB17-Rheology_A0-Mn-C0_1e-1M-NaCl_100%-cone-coverage-2',	#
	'A0-Mn-C10-0.1M-NaCl-1':'20170519-MB17-Rheology_A0-Mn-C10_1e-1M-NaCl_100%-cone-coverage-1',	#
	'A0-Mn-C10-0.1M-NaCl-2':'20170519-MB17-Rheology_A0-Mn-C10_1e-1M-NaCl_100%-cone-coverage-2',	#
	'A0-Mn-C10-0.5M-NaCl-0.9cc':'20170519-MB17-Rheology_A0-Mn-C10_5e-1M-NaCl_90%-cone-coverage-1',	#
	'A0-C10-0.1M-NaCl-1':'20170526-MB17-Rheology_A0-C10_1e-1M-NaCl_100%-cone-coverage-1',		#
	'A0-C10-0.1M-NaCl-2':'20170526-MB17-Rheology_A0-C10_1e-1M-NaCl_100%-cone-coverage-2',		#
	'A0-C10-0.1M-NaCl-3':'20170526-MB17-Rheology_A0-C10_1e-1M-NaCl_100%-cone-coverage-3',		#
	'A0-Zn-C01-0.005M-NaCl':'20170526-MB17-Rheology_A0-Zn-C01_5e-3M-NaCl_100%-cone-coverage-1',	#
	'A0-Zn-C10-0.1M-NaCl-1':'20170526-MB17-Rheology_A0-Zn-C10_1e-1M-NaCl_100%-cone-coverage-1',	#
	'A0-Zn-C10-0.1M-NaCl-2':'20170526-MB17-Rheology_A0-Zn-C10_1e-1M-NaCl_100%-cone-coverage-2',	#
	'A0-Zn-C10-0.1M-NaCl-3':'20170526-MB17-Rheology_A0-Zn-C10_1e-1M-NaCl_100%-cone-coverage-3',	#
	'A0-Zn-C10-0.1M-NaCl-4':'20170526-MB17-Rheology_A0-Zn-C10_1e-1M-NaCl_100%-cone-coverage-4',	#
	'A01-Mn-C0-0.1M-NaCl-0.75cc':'20170526-MB17-Rheology_A01-MnC0_1e-1M-NaCl_75%-cone-coverage-1',	#
	'A01-Zn-C01-0.1M-Nacl-0.90cc':'20170529_MB17_Rheology_A01-Zn-C01_0.1M-NaCl_90%-cone-coverage-1',#
	'A0-C0-0.83M-NaCl-diluted6/5':'20170805-MB17-Rheoloy_A0-C0_6-ml-of-which-5-ml-1M-and-1-ml-0M-salt-1',#
	'A0-C0-icc-ampswp-1':'MB17-A0-C0-not-covered-20rad-sec-ampsweep-1',
	'A0-C0-icc-ampswp-2':'MB17-A0-C0-not-covered-20rad-sec-ampsweep-2',
	'A0-C0-icc-repair-1':'MB17-A0-C0-not-covered-20rad-sec-repair-1',
	'A0-Zn-C10-frqswp-1':'MB17-A0-C10-Zn0-0.05pctstrain-freqsweep-1',
	'A0-Zn-C10-frqswp-2':'MB17-A0-C10-Zn0-0.05pctstrain-freqsweep-duplo-1',
	'A0-Zn0.5-C10-break-1':'MB17-A0-C10-Zn0.5eq-0.05pctstrain-breakit-1',
	'A0-Zn0.5-C10-break-2':'MB17-A0-C10-Zn0.5eq-0.05pctstrain-breakit-2',
	'A0-Zn0.5-C10-frqswp-1':'MB17-A0-C10-Zn0.5eq-0.05pctstrain-freqsweep-duplo-1',
	}
MBpaths={key:path_to_MB+MBpaths[key]+'/' for key in MBpaths}

path_to_lf='/Users/aljosha/stack/PCC-PhD/Data/Rheology/MCR-301/'
lfpaths={ 'lfCC00-pA0-pD0-O-1':'lfCC00/lfCC00-pA0-pD0-O-1',
	'lfCC00-pA01[76]-pD0-ZnII':'lfCC00/lfCC00-pA01[76]-pD0-ZnII-complete-1',
	'lfCC00-pA01[76]-pD0-ZnII-frqswp-1':'lfCC00/lfCC00-pA01[76]-pD0-ZnII-frqswp-1',
	'lfCC00-pA01[91]-pD0-ZnII-frqswp-2-1':'lfCC00/lfCC00-pA01[LF91]-pD00-ZnII-frqswp-duplo-1',
	'lfCC00-pA00-pD01[92]-O-frqswp-2':'lfCC00/lfCC00-pA00-pD01[LF92]-[O]-frqswp-2',
	'lfCC00-pA01[91]-pD0-O-frqswp':'lfCC00/lfCC00-pA01[LF91]-pD00-[O]-nfrc2-1',

	'lfCC02-A0-D0-0.8M-fq-0.5pct-1':'lfCC02-X/lfCC02-pA0[69]-pD0[73]-[0]-0.8M-RAP-frqswp-0.5pct-1',
	'lfCC02-A0-D0-0.8M-fq-0.2pct-1':'lfCC02-X/lfCC02-pA0[69]-pD0[73]-[0]-0.8M-RAP-frqswp-0.2pct-1',
	'lfCC02-A0-D0-0.8M-fq-0.1pct-4':'lfCC02-X/lfCC02-pA0[69]-pD0[73]-[0]-0.8M-RAP-frqswp-0.1pct-4',
	'lfCC02-A0-D0-0.8M-fq-0.1pct-3':'lfCC02-X/lfCC02-pA0[69]-pD0[73]-[0]-0.8M-RAP-frqswp-0.1pct-3',
	'lfCC02-A0-D0-0.8M-fq-0.1pct-2':'lfCC02-X/lfCC02-pA0[69]-pD0[73]-[0]-0.8M-RAP-frqswp-0.1pct-2',
	'lfCC02-A0-D0-0.8M-fq-0.1pct-1':'lfCC02-X/lfCC02-pA0[69]-pD0[73]-[0]-0.8M-RAP-frqswp-0.1pct-1',

	'lfCC02-A01-D01-Mn-0.8M-fq':'lfCC02-X/lfCC02-XH-pA01[76]-pD01[92]-MnII-0.8M-frqswp-0.1pct-1',
	
	'lfCC02-A01-D0-Ni0.8M-fq':'lfCC02-X/lfCC02-X-pA01[76]-pD0[73]-NiII-0.8M-[frqswp-amswp]-1',

	'lfCC02-A01-D0-Zn-0.91M-2':'lfCC02-X/lfCC02-X-pA01[76]-pD0[73]-ZnII-0.91M-[frqswp-ampswp]-2',
	'lfCC02-A01-D01-Ni-0.91M-2':'lfCC02-X/lfCC02-XH-pA01[76]-pD01[92]-NiII-0.91M-[frqswpLONG]0.1pct-2',

	'lfCC04-A01-D0-0.5M-frqswp1':'lfCC04/LFCC04-pA01_94-O-pD_73-frqswp-1',
	'lfCC04-A01-D0-0.5M-frqswp2':'lfCC04/LFCC04-pA01_94-O-pD_73-frqswp-2',
	'lfCC04-A01-D0-0.5M-frqswp3':'lfCC04/LFCC04-pA01_94-O-pD_73-frqswp-3',
	'lfCC04-A01-D0-0.5M-ampswp':'lfCC04/LFCC04-pA01_94-O-pD_73-ampswp-1',
	'lfCC04-A01-D0-0.5M-G_t-1':'lfCC04/LFCC04-pA01_94-O-pD_73-G_t-1',
	'lfCC04-A01-D0-0.5M-G_t-2':'lfCC04/LFCC04-pA01_94-O-pD_73-G_t-2',
	'lfCC04-A01-D0-0.5M-G_t-3':'lfCC04/LFCC04-pA01_94-O-pD_73-G_t-3',
	'lfCC04-A0-D01-Ni-0.91M-frqswp1':'lfCC04/LFCC04-7-pA0_69-Ni-pD01_92-0.91M-frqswp-1',

	'lfCC04-A0-D01-0.5M':'lfCC04/LFCC04-3-pA00_69-O-pD_92-COMPLETE-1',
	'lfCC04-A0-D01-0.5M-G_t':'lfCC04/LFCC04-3-pA00_69-O-pD_92-G_t-1',
	'lfCC04-A0-D01-0.5M-ampswp':'lfCC04/LFCC04-3-pA00_69-O-pD_92-ampswp-ydnfrc-1',
	'lfCC04-A0-D01-0.5M-ampswp-2':'lfCC04/LFCC04-3-pA00_69-O-pD_92-ampswp-ydnfrc-2',

	# X D for Zn
	'lfCC06-A0-Zn-D01-0.91M-frqswp':'lfCC06/LFCC06-2-pA0-Zn-pD01-0.91M-frqswp-1',
	'lfCC06-A0-Zn-D01-0.91M':'lfCC06/LFCC06-2-pA0-Zn-pD01-0.91M-complete-1',

	'lfCC04-A01_94-Zn-D01-0.91M-frqswp1':'lfCC04/LFCC04-5-pA01_94-Zn-pD01_92-0.91M-frqswp-1',
	'lfCC04-A01_94-Zn-D01-0.91M-G_t_1p':'lfCC04/LFCC04-5-pA01_94-Zn-pD01_92-0.91M-G_t_1pct-1',
	'lfCC04-A01_94-Zn-D01-0.91M-G_t_10p-1':'lfCC04/LFCC04-5-pA01_94-Zn-pD01_92-0.91M-G_t_10pct-1',
	'lfCC04-A01_94-Zn-D01-0.91M-G_t_10p-2':'lfCC04/LFCC04-5-pA01_94-Zn-pD01_92-0.91M-G_t_10pct-2',
	'lfCC04-A01_94-Zn-D01-0.91M-G_t_20p-1':'lfCC04/LFCC04-5-pA01_94-Zn-pD01_92-0.91M-G_t_20pct-1',
	'lfCC04-A01_94-Zn-D01-0.91M-G_t_20p-2':'lfCC04/LFCC04-5-pA01_94-Zn-pD01_92-0.91M-G_t_20pct-2',
	'lfCC04-A01_94-Zn-D01-0.91M-G_t_20p-3':'lfCC04/LFCC04-5-pA01_94-Zn-pD01_92-0.91M-G_t_20pct-3',

	'lfCC04-A0-D0-0.99M':'lfCC04/LFCC04-2-pA0_69-pD00_73-0.99M-ACTUALLY-CP50-16804-complete-1',
	
	# X A for Ni. 0.21% of Ni to carboxylic units of pA.
	'A01-Ni0.21-D0-0.91M':'lfCC04/LFCC04-6B-pA01_94-Ni1.1mmol-pD00_73-0.91M-complete-1',
	'A01-Ni0.21-D0-0.91M-ampswp':'lfCC04/LFCC04-6B-pA01_94-Ni1.1mmol-pD00_73-0.91M-ampswp-yldfrc-1',
	'A01-Ni0.21-D0-0.91M-CP50':'lfCC04/LFCC04-6B-pA01_94-Ni1.1mmol-pD00_73-0.91M-CP50-8181-complete',

	# X A for Ni. 0.5% of Ni to carboxylic units of pA.
	'A01_94-Ni-D0-0.91M-frqswp-1':'lfCC04/LFCC04-3-pA01_94-Ni-pD00_73-0.91M-frqswp-1',
	'A01_94-Ni-D0-0.91M-frqswp-2':'lfCC04/LFCC04-3-pA01_94-Ni-pD00_73-0.91M-frqswp-2',
	'A01_94-Ni-D0-0.91M-G_t-1':'lfCC04/LFCC04-3-pA01_94-Ni-pD00_73-0.91M-G_t_25pct-1',
	'A01_94-Ni-D0-0.91M-G_t-2':'lfCC04/LFCC04-3-pA01_94-Ni-pD00_73-0.91M-G_t_25pct-2',
	'A01_94-Ni-D0-0.91M-G_t-3':'lfCC04/LFCC04-3-pA01_94-Ni-pD00_73-0.91M-G_t_25pct-3',
	'A01_94-Ni-D0-0.91M-G_t-4':'lfCC04/LFCC04-3-pA01_94-Ni-pD00_73-0.91M-G_t_25pct-4',
	'A01_94-Ni-D0-0.91M-ampswp':'lfCC04/LFCC04-3-pA01_94-Ni-pD00_73-0.91M-ampswp-1',
	'A01_94-Ni-D0-0.91M-ydnfrc':'lfCC04/LFCC04-3-pA01_94-Ni-pD00_73-0.91M-ydnfrc-1',

	# X D for Ni. 0.5% of Ni to backbone methacrylate ester units of, obviously, pD.
	'lfCC04-A0-D01-Ni-0.91M-frqswp1':'lfCC04/LFCC04-7-pA0_69-Ni-pD01_92-0.91M-frqswp-1',
	'lfCC04-A0-D01-Ni-0.91M-frqswp2':'lfCC04/LFCC04-7-pA0_69-Ni-pD01_92-0.91M-frqswpLONG-G_tLONG-1',
	'lfCC04-A0-D01-Ni-0.91M-lng':'lfCC04/LFCC04-7-pA0_69-Ni-pD01_92-0.91M-frqswpLONG-G_tLONG-2',
	'lfCC04-A0-D01-Ni-0.91M-frqswp3':'lfCC04/LFCC04-7-pA0_69-Ni-pD01_92-0.91M-frqswp_afrchk-1',
	'lfCC04-A0-D01-Ni-0.91M-ampswp':'lfCC04/LFCC04-7-pA0_69-Ni-pD01_92-0.91M-ampswp-ydnfrc-1',
	'lfCC06-A0-D01-Ni-0.8M-ydlong':'lfCC06/LFCC06-4-pA0-Ni-pD01-0.80M-PP25-3d-frqswp-ampswp-ydnfrc-1',
	'lfCC06-A0-D01-Ni-0.8M-long':'lfCC06/LFCC06-4-pA0-Ni-pD01-0.80M-PP25-completelong-2',
	'lfCC06-A0-D01-Ni-0.8M-abr':'lfCC06/LFCC06-4-pA0-Ni-pD01-0.80M-PP25-completelong-1',

	# X H for Ni.
	'lfCC04-A01-D01-Ni-0.91M-frqswp1':'lfCC04/LFCC04-7-pA01_94-Ni-pD01_92-0.91M-frqswp-1',
	'lfCC04-A01-D01-Ni-0.91M-aborted1':'lfCC04/LFCC04-7-pA01_94-Ni-pD01_92-0.91M-COMPLETELONG-1',
	'lfCC04-A01-D01-Ni-0.91M-aborted2':'lfCC04/LFCC04-7-pA01_94-Ni-pD01_92-0.91M-COMPLETELONG-2',
	'lfCC04-A01-D01-Ni-0.91M-aborted3':'lfCC04/LFCC04-7-pA01_94-Ni-pD01_92-0.91M-COMPLETELONG-3',
	'lfCC04-A01-D01-Ni-0.91M-lng':'lfCC04/LFCC04-7-pA01_94-Ni-pD01_92-0.91M-COMPLETELONG-4',
	'lfCC04-A01-D01-Ni-0.91M-ampswp':'lfCC04/LFCC04-7-pA01_94-Ni-pD01_92-0.91M-3dwait-complete-1',
	'lfCC04-A01-D01-Ni-0.91M-ydnfrc':'lfCC04/LFCC04-7-pA01_94-Ni-pD01_92-0.91M-3dwait-ydnfrc-1',
	
	# X D for Co 0.91 M NaCl
	'lfCC06-A0-D01-Co-0.91M-ydnfrc2':'lfCC06/LFCC06-2-pA0-Co-pD01-0.91M-PP25-ydnfrc-2',
	'lfCC06-A0-D01-Co-0.91M-ydnfrc1':'lfCC06/LFCC06-2-pA0-Co-pD01-0.91M-PP25-ydnfrc-1',
	'lfCC06-A0-D01-Co-0.91M-ydampswmp':'lfCC06/LFCC06-2-pA0-Co-pD01-0.91M-PP25-ydampswmp-ydnfrc-1',
	'lfCC06-A0-D01-Co-0.91M-frqswp':'lfCC06/LFCC06-2-pA0-Co-pD01-0.91M-PP25-frqswp-1',
	'lfCC06-A0-D01-Co-0.91M':'lfCC06/LFCC06-2-pA0-Co-pD01-0.91M-PP25-complete-5',
	'lfCC06-A0-D01-Co-0.91M-abt4':'lfCC06/LFCC06-2-pA0-Co-pD01-0.91M-PP25-complete-4',
	'lfCC06-A0-D01-Co-0.91M-abt3':'lfCC06/LFCC06-2-pA0-Co-pD01-0.91M-PP25-complete-3',
	'lfCC06-A0-D01-Co-0.91M-abt2':'lfCC06/LFCC06-2-pA0-Co-pD01-0.91M-PP25-complete-2',
	'lfCC06-A0-D01-Co-0.91M-abt1':'lfCC06/LFCC06-2-pA0-Co-pD01-0.91M-PP25-complete-1',

	# X D for Mn 0.91 M NaCl
	'lfCC06-A0-Mn-D01-0.91M':'lfCC06-pA-Mn-pD01-0.91M/LFCC04-2-pA0_69-pD00_73-0.99M-CP50-16804-complete-1', #mislabeled on measurement
	
	# X H for Ni. LF94C is dialysed against 10 mM EDTA not 100 mM -> check for EDTAlessness.
	'lfCC07-A01-D01-Ni-frqswp':'lfCC07/lfCC07-3-pA00.42_94C-pD01-92-Ni-0.91M-cmp-2',
	'lfCC07-A01-D01-Ni-G_t':'lfCC07/lfCC07-3-pA00.42_94C-pD01-92-Ni-0.91M-cmp-3',
	
	# XSOLO-D for Zn
	'LFCC09-ZnD0184':'LFCC09/LFCC09-ZnoD0184-complete-1',
	# XSOLO-D for Co
	'LFCC09-CoD0184':'LFCC09/LFCC09-CopD0184-complete-2',  # frqswp (2), G_t (3)
	'LFCC09-CoD0184-ampswp':'LFCC09/LFCC09-CopD0184-ampswp-1', # ampswp (1)
	# XSOLO-D for Ni - two samples
	'LFCC09-NiD0184':'LFCC09/LFCC09-NipD0184-complete-1', # frqswp short (1-5), frqswp (6), G_t (7), ampswp (8)
	'LFCC09-NiD0184-S2-frqswp':'LFCC09/LF08CC-NipD0186-S2-frqswp-amspwp-1',
	'LFCC09-NiD0184-S2-ampswp':'LFCC09/LF08CC-NipD0186-S2-frqswp-amspwp-2',
	# XSOLO-D for Mn
	'LFCC10-MnpD86-frqswp':'LFCC09/LFCC10-MnpD86-frqswp2-1',
	'LFCC10-MnpD86-flocrv':'LFCC09/LFCC10-MnpD86-flocrv3-2',

	# LFCC10 - Zn2+ with pA01_95 and pA-pD01_92 re-measurement
	'LFCC10-A01_95-D0-O-frqswp':'LFCC10-MCR501/LFCC10-2BG-pA01_95-pD0-O-frqswp-3', # 2-BKG
	'LFCC10-A01-Zn-D0-0.91M-frqswp':'LFCC10-MCR501/LFCC10-ICC_ALARM-2-pA01_95-pD0-Zn-frqswp-2', # 2-SPL
	'LFCC10-A0-Zn-D01-0.91M':'LFCC10-MCR501/LFCC10-4-pA01_69-pD01_92-Zn4all-complete-1', # 1
	'LFCC10-A0-Zn-D01-0.91M-RPL':'LFCC10-MCR501/LFCC10-4RPL-pA_69-pD01_92-Zn4all-frqswp-ampswp-1', #1 reapplication to do ampswp - the sample is softer due to evap?
	'LFCC10-A01_95-Zn4HLF-D01-0.91M-frqswp':'LFCC10-MCR501/LFCC10-pA01_95-pD01_92-Zn-for-half-frqswp-1', # 3
	'LFCC10-A01_95-Zn4HLF-D01-0.91M-ampswp':'LFCC10-MCR501/LFCC10-pA01_95-pD01_92-Zn-for-half-ampswp-1', # 3
	'LFCC10-A01_95-Zn4HLF-D01-0.91M-G_t':'LFCC10-MCR501/LFCC10-pA01_95-pD01_92-Zn-for-half-G_t-1', # 3
	'LFCC10-A01_95-Zn4ALL-D01-0.91M-G_t':'LFCC10-MCR501/LFCC10-4-pA01_95-pD01_92-Zn4all-G_t-2', # 4
	'LFCC10-A01_95-Zn4ALL-D01-0.91M-ampswp':'LFCC10-MCR501/LFCC10-4-pA01_95-pD01_92-Zn4all-ampswp-1', # 4
	'LFCC10-A01_95-Zn4ALL-D01-0.91M-frqswp':'LFCC10-MCR501/LFCC10-4-pA01_95-pD01_92-Zn4all-complete-1', # 4
}
lfpaths={key:path_to_lf+lfpaths[key]+'/' for key in lfpaths}
paths=merge_two_dicts(lfpaths, MBpaths)
