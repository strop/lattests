import config
import os
import subprocess as subp


pass_on_success = "pass_on_success"
pass_on_error = "pass_on_error"

def run(test_section_title, testdir, subdir, test_pass_type, print_compiler_output = True):
  test_count = 0
  success_count = 0
  failed_test_files = []
  passed_test_files = []
  print "======="
  print test_section_title
  print "======="
  for folder in os.walk(testdir + subdir):
    print "Folder:",folder[0]
    if len(folder[2]) > 0:
      tests = set([x[0] for x in map(lambda x: x.split("."), folder[2])])
      for t in tests:
        if not os.path.exists(folder[0] + "/" + t + config.suffix_src):
          print "Error: nie istnieje plik zrodlowy testu",folder[0],t
        else:
          test_file = t + config.suffix_src
          test_count = test_count + 1
          test_src_path = folder[0] + test_file
          test_bin_path = config.test_bin_dir + "/" + t
          print "Test:",test_src_path,
          compile_out = ""
          try:
            compile_out = subp.check_output([config.compiler_bin, test_src_path], stderr = subp.STDOUT)
            if test_pass_type == pass_on_success:
              print "OK"
              success_count = success_count + 1
              passed_test_files.append(test_file)
            else:
              print "FAILED"
              failed_test_files.append(test_file)
            if print_compiler_output:
              print "Wyjscie z kompilacji:"
              print compile_out
            print
          except OSError as ose:
            print
            print "OSError",ose
          except subp.CalledProcessError as non_zero:
            if test_pass_type == pass_on_error:
              print "OK"
              success_count = success_count + 1
              passed_test_files.append(test_file)
            else:
              print "FAILED"
              failed_test_files.append(test_file)
            print "Kompilacja zakonczyla sie z kodem bledu", non_zero.returncode
            if print_compiler_output:
              print "Wyjscie z kompilacji:"
              print non_zero.output
            print
          pass
  return (test_section_title, success_count, test_count, passed_test_files, failed_test_files)
     # print tests

def clear_results():
  global test_count
  test_count = 0
  global success_count
  success_count = 0

def print_results():
  print success_count,"/",test_count,"zaliczonych testow"
  
test_runs = [
 ("OFFICIAL GOOD", config.official_testdir, config.good_dir, pass_on_success),
 ("OFFICIAL BAD", config.official_testdir, config.bad_dir, pass_on_error),
 ("MINE GOOD", config.my_testdir, config.good_dir, pass_on_success),
 ("MINE BAD", config.my_testdir, config.bad_dir, pass_on_error)
]

results = []

for r in test_runs:
  result = run(r[0], r[1], r[2], r[3])
  results.append(result)

for r in results:
  print r[0],r[1],"/",r[2],("failed: "+str(r[4]) if len(r[4]) > 0 else "all passed :)")
