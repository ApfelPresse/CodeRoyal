

def collisionCheck(entities, acceptableGap):
    """
    return false if everything is ok; true if there was a correction
    """

  return entities.flatMap { u1 ->
    val rad = u1.radius.toDouble()
    val clampDist = if (u1.mass == 0) Constants.OBSTACLE_GAP + rad else rad
    u1.location = u1.location.clampWithin(clampDist, WORLD_WIDTH - clampDist, clampDist, WORLD_HEIGHT - clampDist)

    (entities-u1).map { u2 ->
      val overlap = u1.radius + u2.radius + acceptableGap - u1.location.distanceTo(u2.location).toDouble  // TODO: Fix this?
      if (overlap <= 1e-6) {
        false
      }
      else {
        val (d1, d2) = when {
          u1.mass == 0 && u2.mass == 0 -> Pair(0.5, 0.5)
          u1.mass == 0 -> Pair(0.0, 1.0)
          u2.mass == 0 -> Pair(1.0, 0.0)
          else -> Pair(u2.mass.toDouble() / (u1.mass + u2.mass), u1.mass.toDouble() / (u1.mass + u2.mass))
        }

        val u1tou2 = u2.location - u1.location
        val gap = if (u1.mass == 0 && u2.mass == 0) 20.0 else 1.0

        u1.location -= u1tou2.resizedTo(d1 * overlap + if (u1.mass == 0 && u2.mass > 0) 0.0 else gap)
        u2.location += u1tou2.resizedTo(d2 * overlap + if (u2.mass == 0 && u1.mass > 0) 0.0 else gap)
        true
      }
    }
  }.toList().any { it }
}
