package main

import (
	"bufio"
	"flag"
	"fmt"
	"io/ioutil"
	"os"
	"path"
	"strings"

	"../rest"
)

// form structure for workflow submission
type form struct {
	Filename string `json:"filename"`
}

// ExtractReadFiles : extracts the input files specified in READ seciton
//                    of APBS input file
func ExtractReadFiles(inputContents string) []string {
	var fileNames []string
	readStart := false
	readEnd := false
	scanner := bufio.NewScanner(strings.NewReader(inputContents))

	for i := 0; scanner.Scan(); i++ {
		lineText := strings.TrimSpace(scanner.Text())
		splitLine := strings.Fields(lineText)

		for _, element := range splitLine {
			if strings.ToUpper(element) == "READ" {
				readStart = true
			} else if strings.ToUpper(element) == "END" {
				readEnd = true
			} else {
				fileNames = append(fileNames, element)
			}
			// Break from loop when we've exited READ section
			if readStart && readEnd {
				break
			}
		}
		// Since we've reached the end of the READ section, stop reading file
		if readStart && readEnd {
			break
		}
	}
	// removes the type of file/format from list (e.g. 'charge pqr')
	fileNames = fileNames[2:]

	// check that each file exists
	for _, name := range fileNames {
		if rest.FileExists(name) == false {
			panic("File '" + name + "' does not exist. Specified within READ block of input file")
		}
	}

	return fileNames
}

func main() {
	// debugPtr := flag.Bool("debug", false, "Print debug statements to standard output")
	// Get new job ID if user doesn't specify one
	var jobid string
	flag.StringVar(&jobid, "id", rest.GetNewID(), "Specify custom job identifier for execution. Defaults to randomly generated ID.")
	// jobid = "devTest"

	// TODO: consider whether to print licensing flag from old binaries

	// Check command line arguments
	flag.Parse()
	if flag.NArg() < 1 {
		rest.PrintUsageError("APBS", flag.PrintDefaults, "Not enough arguments: APBS input file required")
		// panic("Not enough arguments: APBS input file required")
	} else {
		var allInputFiles []string

		// verify inputfile's existence
		apbsFileName := flag.Arg(0)
		if rest.FileExists(apbsFileName) == false {
			panic("Input file '" + apbsFileName + "' does not exist")
		}

		// Read input file contents to string
		data, err := ioutil.ReadFile(apbsFileName)
		if err != nil {
			fmt.Print(err)
		}
		inputFileContents := string(data)

		readFileNames := ExtractReadFiles(inputFileContents)
		fmt.Println("File names extracted from", apbsFileName, ":\n", readFileNames)

		// Join input file and READ block files within same list
		allInputFiles = append(allInputFiles, apbsFileName)
		for _, name := range readFileNames {
			allInputFiles = append(allInputFiles, name)
		}

		fmt.Println() // empty line
		fmt.Println(jobid)

		// Upload input files to storage service
		rest.UploadFilesToStorage(allInputFiles, jobid)
		fmt.Println() // empty line

		// Build submission form
		formObj := &form{
			Filename: path.Base(apbsFileName)}

		// Start APBS workflow
		rest.StartWorkflow(jobid, "apbs", *formObj)

		// Wait for completion, get final status
		finalStatus := rest.WaitForExecution(jobid)
		fmt.Printf("Job complete.\n\n")

		// Download output files
		fmt.Printf("Downloading output files:\n")
		for _, file := range finalStatus.Apbs.OutputFiles {
			fmt.Printf("  %s\n", path.Base(file))
			rest.DownloadFile(path.Base(file), jobid)
		}
		fmt.Printf("Finished.\n")

		// Print apbs_output to stdout
		data, err = ioutil.ReadFile("apbs_stdout.txt")
		rest.CheckErr(err)
		os.Stdout.WriteString(string(data))

		// Print error output to stderr
		data, err = ioutil.ReadFile("apbs_stderr.txt")
		rest.CheckErr(err)
		os.Stderr.WriteString(string(data))

	}
}
