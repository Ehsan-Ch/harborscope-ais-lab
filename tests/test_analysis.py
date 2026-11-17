import unittest
from analysis import clean,episodes,state,summary,iso
def p(minute,**kw):return {'vessel':'V001','time':iso(1704067200+minute*60),'lat':33.75,'lon':-118.2,'speed':0.1,'status':5,'kind':'cargo',**kw}
class EpisodeTests(unittest.TestCase):
 def test_observed_duration(self):
  e=episodes([p(0),p(10),p(20)])[0];self.assertEqual(e['minutes'],20);self.assertEqual(e['reports'],3)
 def test_gap_never_counted(self):
  self.assertEqual(episodes([p(0),p(10),p(60),p(70)]),[])
 def test_gap_exactly_at_limit_allowed(self):
  self.assertEqual(episodes([p(0),p(15),p(30)])[0]['minutes'],30)
 def test_moving_splits_stationary_run(self):
  self.assertEqual(episodes([p(0),p(10,speed=2),p(20)]),[])
 def test_status_change_splits_without_bridge(self):
  e=episodes([p(0),p(10),p(20),p(30,status=1),p(40,status=1),p(50,status=1)])
  self.assertEqual([x['state']for x in e],['reported_moored','reported_anchor']);self.assertEqual(sum(x['minutes']for x in e),40)
 def test_vessels_never_join(self):
  self.assertEqual(episodes([p(0),p(10),p(20,vessel='V002')]),[])
 def test_radius_limit_breaks_dwell(self):
  self.assertEqual(episodes([p(0),p(10),p(20,lat=33.76)]),[])
 def test_identical_duplicates_keep_one(self):
  points,q=clean([p(0),p(0)]);self.assertEqual(len(points),1);self.assertEqual(q['identical_duplicates_removed'],1)
 def test_conflicts_reject_all_and_are_order_invariant(self):
  a=[p(0),p(0,speed=1),p(10)];self.assertEqual(clean(a),clean(a[::-1]));self.assertEqual(clean(a)[1]['conflicting_rows_rejected'],2)
 def test_speed_threshold_and_unknown_status(self):
  self.assertEqual(state(p(0,speed=.5)),'reported_moored');self.assertEqual(state(p(0,speed=.51)),'moving');self.assertEqual(state(p(0,status=0)),'other_stationary')
 def test_future_reports_cannot_extend_observed_earlier_run(self):
  a=episodes([p(0),p(10),p(20)]);self.assertEqual(a[0]['minutes'],20);self.assertEqual(episodes([p(0),p(10),p(20),p(30)])[0]['minutes'],30)
 def test_summary_empty_and_median(self):
  self.assertIsNone(summary([])['median_minutes']);e=episodes([p(0),p(10),p(20)]);self.assertEqual(summary(e)['median_minutes'],20)
if __name__=='__main__':unittest.main()
