
class Params:

    # total of 43 parameter
    totalParameter = 44

    # actual list of parameter
    params = [0] * totalParameter

    #util
    maxMaterialValueEndgame = params[0]

    # material
    materialImbalanceMultiplier = params[1]

    # kingSafety 1
    pawnShieldBonusValue = params[2]
    exposedKingPenaltyValue = params[3]
    castledBonusValue = params[4]
    notCastledPenaltyValue = params[5]

    # pawnStructure 5
    isolatedPawnPenaltyValue = params[6]
    doublePawnPenaltyValue = params[7]
    backwardPawnPenaltyValue = params[8]
    passedPawnBonusValue = params[9]
    advancedPassedPawnBonusValue = params[10]
    chainLengthMultiplierBonusValue = params[11]

    # piece activity 11
    mobilityWeightMultiplierBonusValue = params[12]
    pieceCoordinationBonusValue = params[13]
    centralizationBonusValue = params[14]

    # board control 14
    openFileBonusValue = params[15]
    semiOpenBonusValue = params[16]
    openDiagonalBonusValue = params[17]
    centralSquareAttackedBonusValue = params[18]

    # tactical threats 18
    forkBonusValue = params[19]
    pinBonusValue = params[20]
    skewerBonusValue = params[21]

    # engame considerations 21
    kingCenterEndgameBonusValue = params[22]
    pawnKingproximityBonusValue = params[23]
    winningExchangeBonusValue = params[24]
    neutralExchangeBonusValue = params[25]

    # space and control 25
    spaceAdvantageMultiplierBonusValue = params[26]
    zugzwangBonusValue = params[27]

    # pawn dynamics 27
    pawnBreakBonusValue = params[28]
    pawnBreakWithKingExposureBonusValue = params[29]
    structureBonusValue = params[30]

    # piece exchange 30
    exchangeScoreBonusValue = params[31]
    exchangeScorePenaltyValue = params[32]
    strongCompensationThresholdValue = params[33]
    strongSacrificeBonusValue = params[34]
    mediumCompensationThresholdValue = params[35]
    mediumSacrificeBonusValue = params[36]

    # threats 36
    strongThreatBonusValue = params[37]
    mediumThreatBonusValue = params[38]
    weakThreatBonusValue = params[39]

    # special case 39
    backRankBonusValue = params[40]
    backRankPenaltyValue = params[41]
    promotionScoreBonusValue = params[42]
    promotionPossibilityBonusValue = params[43]