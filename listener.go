package main

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strings"
)

func activateCondaEnv(envName string) *exec.Cmd {
	var cmd *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		cmd = exec.Command("cmd", "/c", "conda", "activate", envName)
	default:
		cmd = exec.Command("bash", "-c", "conda activate "+envName)
	}
	return cmd
}

func main() {
	condaEnvName := "nefis2nc"
	folderPath := "D:/Sea4cast/Sea4cast/Delft3D-sample/For Hengkek/Sample setup and simulation/"
	outputPath := filepath.Join(".", "tests/testdata")

	// Activate Conda environment
	activateCmd := activateCondaEnv(condaEnvName)
	activateCmd.Stdout = os.Stdout
	activateCmd.Stderr = os.Stderr
	err := activateCmd.Run()
	if err != nil {
		fmt.Println("Error activating Conda environment:", err)
		return
	}

	var (
		trihDatFile    string
		trihDefFile    string
		trimDatFile    string
		trimDefFile    string
		outputTrihFile = filepath.Join(outputPath, "test-trih.nc")
		outputTrimFile = filepath.Join(outputPath, "test-trim.nc")
	)

	// Iterate through the files in the folder
	filepath.Walk(folderPath, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			fmt.Println(err)
			return err
		}

		if info.IsDir() {
			return nil
		}

		filename := info.Name()
		if (strings.HasPrefix(filename, "trih") || strings.HasPrefix(filename, "trim")) &&
			(strings.HasSuffix(filename, ".dat") || strings.HasSuffix(filename, ".def")) {

			switch {
			case strings.HasSuffix(filename, ".dat"):
				if strings.HasPrefix(filename, "trih") {
					trihDatFile = path
				} else if strings.HasPrefix(filename, "trim") {
					trimDatFile = path
				}
			case strings.HasSuffix(filename, ".def"):
				if strings.HasPrefix(filename, "trih") {
					trihDefFile = path
				} else if strings.HasPrefix(filename, "trim") {
					trimDefFile = path
				}
			}
		}

		return nil
	})

	fmt.Println("trihDatFile:", trihDatFile)
	fmt.Println("trihDefFile:", trihDefFile)
	fmt.Println("trimDatFile:", trimDatFile)
	fmt.Println("trimDefFile:", trimDefFile)

	// Check if trihDatFile and trihDefFile are not empty
	if trihDatFile != "" && trihDefFile != "" {
		cmd := exec.Command("python", "trih2nc.py", trihDatFile, trihDefFile, outputTrihFile)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		err := cmd.Run()
		if err != nil {
			fmt.Println("Error running trih2nc.py:", err)
		}
	}

	if trimDatFile != "" && trimDefFile != "" {
		cmd := exec.Command("python", "trim2nc.py", trimDatFile, trimDefFile, outputTrimFile)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		err := cmd.Run()
		if err != nil {
			fmt.Println("Error running trim2nc.py:", err)
		}
	}
}
