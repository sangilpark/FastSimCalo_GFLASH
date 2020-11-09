import os, sys
import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

process = cms.Process("PROD")
process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.load("IOMC.EventVertexGenerators.VtxSmearedGauss_cfi")
process.load("Geometry.CMSCommonData.ecalhcalGeometryXML_cfi")
process.load("Geometry.HcalCommonData.hcalParameters_cfi")
process.load("Geometry.HcalCommonData.hcalDDDSimConstants_cfi")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.EventContent.EventContent_cff")
process.load('Configuration.StandardSequences.Generator_cff')
process.load('Configuration.StandardSequences.SimIdeal_cff')
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
from Configuration.AlCa.autoCond import autoCond
process.GlobalTag.globaltag = autoCond['run2_mc']

#process.MessageLogger = cms.Service("MessageLogger",
#    debugModules = cms.untracked.vstring('*'),
#    cout = cms.untracked.PSet(
#        INFO = cms.untracked.PSet(
#            limit = cms.untracked.int32(-1)
#        ),
#        EcalGeom = cms.untracked.PSet(
#            limit = cms.untracked.int32(0)
#        ),
#        MagneticField = cms.untracked.PSet(
#            limit = cms.untracked.int32(0)
#        ),
#        CaloSim = cms.untracked.PSet(
#            limit = cms.untracked.int32(0)
#        ),
#        DEBUG = cms.untracked.PSet(
#            limit = cms.untracked.int32(0)
#        ),
#        G4cerr = cms.untracked.PSet(
#            limit = cms.untracked.int32(-1)
#        ),
#        HCalGeom = cms.untracked.PSet(
#            limit = cms.untracked.int32(0)
#        ),
#        threshold = cms.untracked.string('DEBUG'),
#        HFShower = cms.untracked.PSet(
#            limit = cms.untracked.int32(0)
#        ),
#        G4cout = cms.untracked.PSet(
#            limit = cms.untracked.int32(-1)
#        ),
#        SimG4CoreApplication = cms.untracked.PSet(
#            limit = cms.untracked.int32(-1)
#        ),
#        HcalSim = cms.untracked.PSet(
#            limit = cms.untracked.int32(-1)
#        ),
#        EcalSim = cms.untracked.PSet(
#            limit = cms.untracked.int32(0)
#        )
#    ),
#    categories = cms.untracked.vstring(
#        'CaloSim', 
#        'EcalGeom', 
#        'EcalSim', 
#        'HCalGeom', 
#        'HcalSim',
#        'HFShower', 
#        'SimG4CoreApplication', 
#        'G4cout', 
#        'G4cerr', 
#        'MagneticField'
#    ),
#    destinations = cms.untracked.vstring('cout')
#)

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

# register options
options.register ('energy',
                  100, # default value
                  VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                  VarParsing.VarParsing.varType.int,          # string, int, or float
                  "Incident Energy for gun particle")

options.register ('saveHits',
                  False, # default value
                  VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                  VarParsing.VarParsing.varType.bool,          # string, int, or float
                  "Boolean for saveHits")

# get and parse the command line arguments
options.parseArguments()

print options.maxEvents, options.energy, options.saveHits

process.load("IOMC.RandomEngine.IOMC_cff")
process.RandomNumberGeneratorService.generator.initialSeed = 456789
process.RandomNumberGeneratorService.g4SimHits.initialSeed = 9876
process.RandomNumberGeneratorService.VtxSmeared.initialSeed = 123456789

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(500)
)

process.source = cms.Source("EmptySource",
    firstRun        = cms.untracked.uint32(1),
    firstEvent      = cms.untracked.uint32(1)
)

process.generator = cms.EDProducer("FlatRandomEGunProducer",
    PGunParameters = cms.PSet(
        PartID = cms.vint32(211),
        MinEta = cms.double(-0.05),
        MaxEta = cms.double(0.05),
        MinPhi = cms.double(-3.14159265359),
        MaxPhi = cms.double(3.14159265359),
        #MinE   = cms.double(99.99),
        #MaxE   = cms.double(100.01)
        MinE   = cms.double(options.energy-0.01),
        MaxE   = cms.double(options.energy+0.01)
    ),
    Verbosity       = cms.untracked.int32(0),
    AddAntiParticle = cms.bool(False)
)

#process.output = cms.OutputModule("PoolOutputModule",
#    process.FEVTSIMEventContent,
#    fileName = cms.untracked.string('simevent.root')
#)

#process.Timing = cms.Service("Timing")

#process.Tracer = cms.Service("Tracer")

process.generation_step = cms.Path(process.pgen)
process.simulation_step = cms.Path(process.psim)
#process.out_step = cms.EndPath(process.output)

process.TFileService = cms.Service("TFileService",
    #fileName = cms.string('RezaAnalysis.root')
    fileName = cms.string('RezaAnalysis_{}GeV.root'.format(options.energy))
)
process.g4SimHits.Physics.type = 'SimG4Core/Physics/QGSP_BERT_EML'
process.g4SimHits.G4Commands = ['/tracking/verbose 1']
#process.common_maximum_timex = cms.PSet(
#    MaxTrackTime  = cms.double(1000.0),
#    MaxTimeNames  = cms.vstring(),
#    MaxTrackTimes = cms.vdouble(),
#    DeadRegions   = cms.vstring(),
#    CriticalEnergyForVacuum = cms.double(2.0),
#    CriticalDensity         = cms.double(1e-15)
#)
#process.g4SimHits.StackingAction = cms.PSet(
#    process.common_heavy_suppression,
#    process.common_maximum_timex,
#    TrackNeutrino = cms.bool(False),
#    KillDeltaRay  = cms.bool(False),
#    KillHeavy     = cms.bool(False),
#    KillGamma     = cms.bool(False),
#    GammaThreshold= cms.double(0.0001),  ## (MeV)
#    SaveFirstLevelSecondary = cms.untracked.bool(True),
#    SavePrimaryDecayProductsAndConversionsInTracker = cms.untracked.bool(True),
#    SavePrimaryDecayProductsAndConversionsInCalo    = cms.untracked.bool(True),
#    SavePrimaryDecayProductsAndConversionsInMuon    = cms.untracked.bool(True),
#        RusRoGammaEnergyLimit  = cms.double(5.0), ## (MeV)
#        RusRoEcalGamma         = cms.double(0.3),
#        RusRoHcalGamma         = cms.double(0.3),
#        RusRoMuonIronGamma     = cms.double(0.3),
#        RusRoPreShowerGamma    = cms.double(0.3),
#        RusRoCastorGamma       = cms.double(0.3),
#        RusRoWorldGamma        = cms.double(0.3),
#        RusRoNeutronEnergyLimit= cms.double(10.0), ## (MeV)
#        RusRoEcalNeutron       = cms.double(0.1),
#        RusRoHcalNeutron       = cms.double(0.1),
#        RusRoMuonIronNeutron   = cms.double(0.1),
#        RusRoPreShowerNeutron  = cms.double(0.1),
#        RusRoCastorNeutron     = cms.double(0.1),
#        RusRoWorldNeutron      = cms.double(0.1),
#        RusRoProtonEnergyLimit = cms.double(0.0),
#        RusRoEcalProton        = cms.double(1.0),
#        RusRoHcalProton        = cms.double(1.0),
#        RusRoMuonIronProton    = cms.double(1.0),
#        RusRoPreShowerProton   = cms.double(1.0),
#        RusRoCastorProton      = cms.double(1.0),
#        RusRoWorldProton       = cms.double(1.0)
#)
#process.g4SimHits.SteppingAction = cms.PSet(
#    process.common_maximum_timex,
#    EkinNames               = cms.vstring(),
#    EkinThresholds          = cms.vdouble(),
#    EkinParticles           = cms.vstring(),
#    Verbosity               = cms.untracked.int32(0)
#)
process.g4SimHits.Watchers = cms.VPSet(cms.PSet(
    HcalQie = cms.PSet(
        NumOfBuckets = cms.int32(10),
        BaseLine = cms.int32(4),
        BinOfMax = cms.int32(6),
        PreSamples = cms.int32(0),
        EDepPerPE = cms.double(0.0005),
        SignalBuckets = cms.int32(2),
        SigmaNoise = cms.double(0.5),
        qToPE = cms.double(4.0)
    ),
    type = cms.string('CaloShowerProfile'),
    CaloShowerProfile = cms.PSet(
        Eta0 = cms.double(0.0),
        FileName = cms.string('CaloShower_output.root'),
        Phi0 = cms.double(0.0),
        #saveHits = cms.bool(False)
        saveHits = cms.bool(options.saveHits)
    )
))

# Schedule definition 
process.schedule = cms.Schedule(process.generation_step,
                                process.simulation_step
#                                process.out_step
                                )

# filter all path with the production filter sequence
for path in process.paths:
        getattr(process,path)._seq = process.generator * getattr(process,path)._seq
