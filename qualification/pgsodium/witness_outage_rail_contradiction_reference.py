"""IE-W07/W08 reference: never infer external settlement from local commitment.

The witness receives independently verified rail status, not a caller-supplied
COMMITTED claim. This pure policy test is not an actual rail integration.
"""
def classify(local_commit, witness_available, verified_rail):
    if not witness_available:
        return "REFUSED_WITNESS_UNAVAILABLE"
    if verified_rail not in ("SETTLED", "REJECTED", "UNKNOWN"):
        return "UNRESOLVED_UNVERIFIED_RAIL"
    if verified_rail == "UNKNOWN":
        return "UNRESOLVED_RAIL_OUTCOME"
    if local_commit and verified_rail == "REJECTED":
        return "CONTRADICTORY_LOCAL_COMMIT_RAIL_REJECTED"
    if not local_commit and verified_rail == "SETTLED":
        return "CONTRADICTORY_RAIL_SETTLED_WITHOUT_LOCAL_COMMIT"
    if local_commit and verified_rail == "SETTLED":
        return "SETTLED_REFERENCE_ONLY"
    return "REJECTED_REFERENCE_ONLY"

def main():
    assert classify(True,False,"SETTLED")=="REFUSED_WITNESS_UNAVAILABLE"
    print("IE-W07 OUTAGE: witness unavailable -> REFUSED_WITNESS_UNAVAILABLE")
    assert classify(True,True,"UNKNOWN")=="UNRESOLVED_RAIL_OUTCOME"
    print("IE-W07 UNKNOWN: local COMMITTED plus unknown rail -> UNRESOLVED_RAIL_OUTCOME")
    assert classify(True,True,"CALLER_SAYS_SETTLED")=="UNRESOLVED_UNVERIFIED_RAIL"
    print("IE-W07 UNVERIFIED: caller settlement claim -> UNRESOLVED_UNVERIFIED_RAIL")
    assert classify(True,True,"REJECTED")=="CONTRADICTORY_LOCAL_COMMIT_RAIL_REJECTED"
    print("IE-W08 CONTRADICTION: local COMMITTED versus rail REJECTED -> explicit contradiction")
    assert classify(False,True,"SETTLED")=="CONTRADICTORY_RAIL_SETTLED_WITHOUT_LOCAL_COMMIT"
    print("IE-W08 CONTRADICTION: rail SETTLED without local commitment -> explicit contradiction")
    print("LIMITATION: pure reference policy; rail status is simulated, not authenticated or observed; no external consequence evidence")

if __name__=="__main__":main()
