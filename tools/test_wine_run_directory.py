"""Back-to-back preflight/runtime starts must retain both evidence directories."""
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import qualify_integrated_wine as q
class RunDirectories(unittest.TestCase):
    def test_two_starts_in_same_second_are_distinct(self):
        with tempfile.TemporaryDirectory() as d,patch.object(q.time,"strftime",return_value="fixed"):
            root=Path(d)
            def make():
                if hasattr(q,"make_run_directory"):return q.make_run_directory(root,"one")
                line=next(l.strip() for l in Path(q.__file__).read_text().splitlines() if l.strip().startswith("E=runtime/"))
                class Args:stage="one"
                env={"runtime":root,"args":Args(),"time":q.time}
                exec(line,env)
                return env["E"]
            first=make();(first/"evidence").write_text("preserve")
            second=make()
            self.assertNotEqual(first,second)
            self.assertEqual((first/"evidence").read_text(),"preserve")
if __name__=="__main__":unittest.main()
