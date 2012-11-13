#!/usr/bin/env python
import config
import os
import subprocess as subp

pass_on_success = "pass_on_success"
pass_on_error = "pass_on_error"

def run(test_section_title, testdir, subdir, test_pass_type, print_compiler_output = False, run_io_phase = True):
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
        io_phase_succeeded = True
        compilation_phase_succeeded = False
        test_count = test_count + 1
        test_file = t + config.suffix_src
        input_file = t + config.suffix_in
        output_file = t + config.suffix_out
        test_src_path = folder[0] + test_file
        test_bin_path = config.test_bin_dir + "/" + t
        test_input_path = folder[0] + "/" + input_file
        test_output_path = folder[0] + "/" + output_file

        if not os.path.exists(folder[0] + "/" + t + config.suffix_src):
          print "Blad: nie istnieje plik zrodlowy testu",folder[0],t
        else:
          print "Test:",test_src_path,
          compile_out = ""
          try:
            compile_out = subp.check_output([config.compiler_bin, test_src_path], stderr = subp.STDOUT)
            if test_pass_type == pass_on_success:
              print "OK"
              compilation_phase_succeeded = True
            else:
              print "FAILED"
              compilation_phase_succeeded = False
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
              compilation_phase_succeeded = True
            else:
              print "FAILED"
              compilation_phase_succeeded = False
            print "Kompilacja zakonczyla sie z kodem bledu", non_zero.returncode
            if print_compiler_output:
              print "Wyjscie z kompilacji:"
              print non_zero.output
            print
        # sprawdzanie i/o
        if os.path.exists(test_input_path) and run_io_phase:
          if not os.path.exists(test_output_path):
            print "Blad: nie istnieje plik wynikowy dla pliku wejsciowego", input_file
            output = subp.check_output("test_bin_path" + " < " + test_input_path, shell=True)
            expected_output = file(test_output_path).read()
            if output != expected_output:
              print "FAILED"
              print "oczekiwano:"
              print expected_output
              print "otrzymano:"
              print output
              io_phase_succeeded = False
            else:
              io_phase_succeeded = True
        if ((not run_io_phase) or io_phase_succeeded) and compilation_phase_succeeded:
          success_count = success_count + 1
          passed_test_files.append(test_file)
        else:
          failed_test_files.append(test_file)
  return (test_section_title, success_count, test_count, passed_test_files, failed_test_files)

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
