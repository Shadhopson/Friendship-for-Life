SELECT
  GameState.Time,
  GameState.Round,
  GameState.Money,
  GameState.FinalScore,
  GameStateAction.ActionType,
  GameStateAction.Decision,
  C1.ChildCode AS ChildCode1,
  C2.ChildCode AS ChildCode2,
  C3.ChildCode AS ChildCode3,
  ( C1.ChildCode || CASE WHEN  C2.ChildCode  IS NOT NULL THEN  C2.ChildCode  ELSE "" END || CASE WHEN  C3.ChildCode  IS NOT NULL THEN  C3.ChildCode  ELSE "" END ) AS AllChildren,
  J1.JobCode AS JobCode1,
  J2.JobCode AS JobCode2,
  J3.JobCode AS JobCode3,
  ( J1.JobCode || CASE WHEN  J2.JobCode  IS NOT NULL THEN  J2.JobCode  ELSE "" END || CASE WHEN  J3.JobCode  IS NOT NULL THEN  J3.JobCode  ELSE "" END ) AS AllJob,
  H1.HobbyCode AS HobbyCode1,
  H2.HobbyCode AS HobbyCode2,
  H3.HobbyCode AS HobbyCode3,
  ( H1.HobbyCode || CASE WHEN  H2.HobbyCode  IS NOT NULL THEN  H2.HobbyCode  ELSE "" END || CASE WHEN  H3.HobbyCode  IS NOT NULL THEN  H3.HobbyCode  ELSE "" END ) AS AllHobby,
  P1.PartnerCode AS PartnerCode1,
  P2.PartnerCode AS PartnerCode2,
  P3.PartnerCode AS PartnerCode3,
  ( P1.PartnerCode || CASE WHEN  P2.PartnerCode  IS NOT NULL THEN  P2.PartnerCode  ELSE "" END || CASE WHEN  P3.PartnerCode  IS NOT NULL THEN  P3.PartnerCode  ELSE "" END ) AS AllPartner,

  FP1.PartnerCode AS FailedPartnerCode1,
  FP2.PartnerCode AS FailedPartnerCode2,
  FP3.PartnerCode AS FailedPartnerCode3,
  ( FP1.PartnerCode || CASE WHEN  FP2.PartnerCode  IS NOT NULL THEN  FP2.PartnerCode  ELSE "" END || CASE WHEN  FP3.PartnerCode  IS NOT NULL THEN  FP3.PartnerCode  ELSE "" END ) AS AllFailedPartner,
  PP1.PartnerCode AS PassedPartnerCode1,
  PP2.PartnerCode AS PassedPartnerCode2,
  PP3.PartnerCode AS PassedPartnerCode3,
  ( PP1.PartnerCode || CASE WHEN  PP2.PartnerCode  IS NOT NULL THEN  PP2.PartnerCode  ELSE "" END || CASE WHEN  PP3.PartnerCode  IS NOT NULL THEN  PP3.PartnerCode  ELSE "" END ) AS AllPassedPartner
FROM
  GameState
  INNER JOIN GameStateAction ON GameStateAction.GameStateId = GameState.GameStateId
  LEFT JOIN GameStateChild AS C1 ON C1.GameStateId = GameState.GameStateId AND C1.Position=1
  LEFT JOIN GameStateChild AS C2 ON C2.GameStateId = GameState.GameStateId AND C2.Position=2
  LEFT JOIN GameStateChild AS C3 ON C3.GameStateId = GameState.GameStateId AND C3.Position=3
  LEFT JOIN GameStateJob AS J1 ON J1.GameStateId = GameState.GameStateId AND J1.Position=1
  LEFT JOIN GameStateJob AS J2 ON J2.GameStateId = GameState.GameStateId AND J2.Position=2
  LEFT JOIN GameStateJob AS J3 ON J3.GameStateId = GameState.GameStateId AND J3.Position=3
  LEFT JOIN GameStateHobby AS H1 ON H1.GameStateId = GameState.GameStateId AND H1.Position=1
  LEFT JOIN GameStateHobby AS H2 ON H2.GameStateId = GameState.GameStateId AND H2.Position=2
  LEFT JOIN GameStateHobby AS H3 ON H3.GameStateId = GameState.GameStateId AND H3.Position=3
  LEFT JOIN GameStatePartner AS P1 ON P1.GameStateId = GameState.GameStateId AND P1.Position=1
  LEFT JOIN GameStatePartner AS P2 ON P2.GameStateId = GameState.GameStateId AND P2.Position=2
  LEFT JOIN GameStatePartner AS P3 ON P3.GameStateId = GameState.GameStateId AND P3.Position=3

  LEFT JOIN GameStateJobFiredCount AS PJ1 ON PJ1.GameStateId = GameState.GameStateId AND PJ1.Position=1
  LEFT JOIN GameStateJobFiredCount AS PJ2 ON PJ2.GameStateId = GameState.GameStateId AND PJ2.Position=2
  LEFT JOIN GameStateJobFiredCount AS PJ3 ON PJ3.GameStateId = GameState.GameStateId AND PJ3.Position=3
  LEFT JOIN GameStateJobPassedCount AS FJ1 ON FJ1.GameStateId = GameState.GameStateId AND FJ1.Position=1
  LEFT JOIN GameStateJobPassedCount AS FJ2 ON FJ2.GameStateId = GameState.GameStateId AND FJ2.Position=2
  LEFT JOIN GameStateJobPassedCount AS FJ3 ON FJ3.GameStateId = GameState.GameStateId AND FJ3.Position=3
  LEFT JOIN GameStatePartnerFiredCount AS PP1 ON PP1.GameStateId = GameState.GameStateId AND PP1.Position=1
  LEFT JOIN GameStatePartnerFiredCount AS PP2 ON PP2.GameStateId = GameState.GameStateId AND PP2.Position=2
  LEFT JOIN GameStatePartnerFiredCount AS PP3 ON PP3.GameStateId = GameState.GameStateId AND PP3.Position=3
  LEFT JOIN GameStatePartnerPassedCount AS FP1 ON FP1.GameStateId = GameState.GameStateId AND FP1.Position=1
  LEFT JOIN GameStatePartnerPassedCount AS FP2 ON FP2.GameStateId = GameState.GameStateId AND FP2.Position=2
  LEFT JOIN GameStatePartnerPassedCount AS FP3 ON FP3.GameStateId = GameState.GameStateId AND FP3.Position=3

