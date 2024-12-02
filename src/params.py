import numpy as np

class Params:

    # total of 43 parameter
    totalParameter = 44

    # actual list of parameter
    params = np.random.uniform(2, -2, size=totalParameter).astype(np.float64)
    #util
    maxMaterialValueEndgame = lambda: Params.params[0]

    # material
    materialImbalanceMultiplier = lambda: Params.params[1]

    # kingSafety 1
    pawnShieldBonusValue = lambda: Params.params[2]
    exposedKingPenaltyValue = lambda: Params.params[3]
    castledBonusValue = lambda: Params.params[4]
    notCastledPenaltyValue = lambda: Params.params[5]

    # pawnStructure 5
    isolatedPawnPenaltyValue = lambda: Params.params[6]
    doublePawnPenaltyValue = lambda: Params.params[7]
    backwardPawnPenaltyValue = lambda: Params.params[8]
    passedPawnBonusValue = lambda: Params.params[9]
    advancedPassedPawnBonusValue = lambda: Params.params[10]
    chainLengthMultiplierBonusValue = lambda: Params.params[11]

    # piece activity 11
    mobilityWeightMultiplierBonusValue = lambda: Params.params[12]
    pieceCoordinationBonusValue = lambda: Params.params[13]
    centralizationBonusValue = lambda: Params.params[14]

    # board control 14
    openFileBonusValue = lambda: Params.params[15]
    semiOpenBonusValue = lambda: Params.params[16]
    openDiagonalBonusValue = lambda: Params.params[17]
    centralSquareAttackedBonusValue = lambda: Params.params[18]

    # tactical threats 18
    forkBonusValue = lambda: Params.params[19]
    pinBonusValue = lambda: Params.params[20]
    skewerBonusValue = lambda: Params.params[21]

    # engame considerations 21
    kingCenterEndgameBonusValue = lambda: Params.params[22]
    pawnKingproximityBonusValue = lambda: Params.params[23]
    winningExchangeBonusValue = lambda: Params.params[24]
    neutralExchangeBonusValue = lambda: Params.params[25]

    # space and control 25
    spaceAdvantageMultiplierBonusValue = lambda: Params.params[26]
    zugzwangBonusValue = lambda: Params.params[27]

    # pawn dynamics 27
    pawnBreakBonusValue = lambda: Params.params[28]
    pawnBreakWithKingExposureBonusValue = lambda: Params.params[29]
    structureBonusValue = lambda: Params.params[30]

    # piece exchange 30
    exchangeScoreBonusValue = lambda: Params.params[31]
    exchangeScorePenaltyValue = lambda: Params.params[32]
    strongCompensationThresholdValue = lambda: Params.params[33]
    strongSacrificeBonusValue = lambda: Params.params[34]
    mediumCompensationThresholdValue = lambda: Params.params[35]
    mediumSacrificeBonusValue = lambda: Params.params[36]

    # threats 36
    strongThreatBonusValue = lambda: Params.params[37]
    mediumThreatBonusValue = lambda: Params.params[38]
    weakThreatBonusValue = lambda: Params.params[39]

    # special case 39
    backRankBonusValue = lambda: Params.params[40]
    backRankPenaltyValue = lambda: Params.params[41]
    promotionScoreBonusValue = lambda: Params.params[42]
    promotionPossibilityBonusValue = lambda: Params.params[43]