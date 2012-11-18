#!/usr/bin/env python
import config
import os
import subprocess as subp

pass_on_success = "pass_on_success"
pass_on_error = "pass_on_error"

def run(test_section_title, testdir, subdir, test_pass_type, print_compiler_output = True, run_io_phase = True):
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
      tests = sorted(list(set([x[0] for x in map(lambda x: x.split("."), folder[2])])))
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

        compiler_stdout = ""
        compiler_stderr = ""
        compiler_returncode = ""

        test_info = []
        
        if not os.path.exists(folder[0] + "/" + t + config.suffix_src):
          test_info.append("Blad: nie istnieje plik zrodlowy testu "+folder[0]+" "+t)
        else:
          compile_out = ""
          try:
            compiler_process = subp.Popen([config.compiler_bin, test_src_path], stdout = subp.PIPE, stderr = subp.PIPE)
            (compiler_stdout, compiler_stderr) = compiler_process.communicate()
            stderr_lines = compiler_stderr.splitlines()

            if compiler_process.returncode == 0:
              if test_pass_type == pass_on_success:
                if stderr_lines[0] == "OK":
                  compilation_phase_succeeded = True
                else:
                  test_info.append("Kompilator nie wypisal \"OK\" w pierwszej linii stderr")
            else: # non-zero return code
              test_info.append("Kompilacja zakonczyla sie kodem bledu " + str(compiler_process.returncode))
              if test_pass_type == pass_on_error:
                if stderr_lines[0] == "ERROR":
                  compilation_phase_succeeded = True
                else:
                  test_info.append("Kompilator nie wypisal \"ERROR\" w pierwszej linii stderr")
            if print_compiler_output:
              test_info.append("Wyjscie err z kompilacji:")
              test_info.append(compiler_stderr)
              test_info.append("Wyjscie std z kompilacji:")
              test_info.append(compiler_stdout)
            print
          except OSError as ose:
            test_info.append("OSError")
            test_info.append(str(ose))
        # sprawdzanie i/o
        if os.path.exists(test_input_path) and run_io_phase:
          if not os.path.exists(test_output_path):
            print "Blad: nie istnieje plik wynikowy dla pliku wejsciowego", input_file
            output = subp.check_output("test_bin_path" + " < " + test_input_path, shell=True)
            expected_output = file(test_output_path).read()
            if output != expected_output:
              print "I/O TEST FAILED"
              print "oczekiwano:"
              print expected_output
              print "otrzymano:"
              print output
              io_phase_succeeded = False
            else:
              io_phase_succeeded = True

        print "Test:", test_src_path,
        if ((not run_io_phase) or io_phase_succeeded) and compilation_phase_succeeded:
          success_count = success_count + 1
          print "OK"
          passed_test_files.append(test_file)
        else:
          print "FAILED"
          failed_test_files.append(test_file)
        print "\n".join(test_info)
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
 ("JACEK GOOD", config.jackowy_testdir, config.good_dir, pass_on_success),
 ("JACEK BAD", config.jackowy_testdir, config.bad_dir, pass_on_error),
 ("MINE GOOD", config.my_testdir, config.good_dir, pass_on_success),
 ("MINE BAD", config.my_testdir, config.bad_dir, pass_on_error)
]

results = []

for r in test_runs:
  result = run(r[0], r[1], r[2], r[3])
  results.append(result)

for r in results:
  print r[0],r[1],"/",r[2],("failed: "+str(r[4]) if len(r[4]) > 0 else "all passed :)")
