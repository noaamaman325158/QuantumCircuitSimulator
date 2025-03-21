import logging

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.qasm2.exceptions import QASM2ParseError

from app.main.exceptions.custom_exceptions import QASMParsingError, CircuitExecutionError
from app.main.app import logger

class QuantumCircuitService:
    """
    Service for creating, executing, and processing quantum circuits.
    """

    def __init__(self, shots=10000):
        """
        Initialize the quantum circuit service.
        """
        self.shots = shots
        self.simulator = AerSimulator()
        logger.info(f"Initialized QuantumCircuitService with {shots} shots")

    async def execute_qasm(self, qasm_string):
        """
        Execute a quantum circuit from QASM string.
        """
        try:
            processed_qasm = self._preprocess_qasm(qasm_string)
            logger.info(f"Processed QASM string:\n{processed_qasm}")

            circuit = QuantumCircuit.from_qasm_str(processed_qasm)
            logger.info(f"Successfully parsed QASM string into circuit with {circuit.num_qubits} qubits")

            job = self.simulator.run(circuit, shots=self.shots)
            result = job.result()
            counts = result.get_counts(circuit)

            logger.info(f"Circuit execution complete with {len(counts)} unique outcomes")
            formatted_counts = self.format_counts(counts)
            return {"error": False, "counts": formatted_counts}

        except QASM2ParseError as e:
            logger.error(f"QASM parsing failed. Error: {str(e)}")
            raise QASMParsingError(message=str(e))
        except QASMParsingError as e:
            logger.error(f"QASM parsing failed. Error: {str(e)}")
            return {"error": True, "message": str(e)}
        except CircuitExecutionError as e:
            logger.error(f"Circuit execution failed. Error: {str(e)}")
            return {"error": True, "message": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise CircuitExecutionError(message=str(e))

    def _preprocess_qasm(self, qasm_string):
        """
        Preprocess QASM string to ensure compatibility.
        """
        try:
            # Handle QASM 3.0 to 2.0 conversion
            if "OPENQASM 3.0" in qasm_string:
                logger.info("Converting QASM 3.0 to QASM 2.0 format")

                lines = qasm_string.strip().split('\n')
                processed_lines = []

                for line in lines:
                    line = line.strip()

                    if "OPENQASM 3.0" in line:
                        processed_lines.append("OPENQASM 2.0;")
                        processed_lines.append('include "qelib1.inc";')
                        continue

                    if line.startswith("qubit[") or line.startswith("bit["):
                        line = line.replace("qubit[", "qreg q[").replace("bit[", "creg c[")

                    if " = measure " in line:
                        line = line.replace(" = measure ", " measure ")

                    processed_lines.append(line)

                processed_qasm = '\n'.join(processed_lines)
                return processed_qasm

            if "OPENQASM 2.0" in qasm_string and 'include "qelib1.inc"' not in qasm_string:
                lines = qasm_string.strip().split('\n')
                for i, line in enumerate(lines):
                    if "OPENQASM 2.0" in line:
                        lines.insert(i + 1, 'include "qelib1.inc";')
                        break
                return '\n'.join(lines)

            return qasm_string

        except Exception as e:
            raise QASMParsingError(message=str(e), original_qasm=qasm_string)

    def format_counts(self, counts):
        """
        Format counts for API response.
        """
        if not counts:
            return {}

        formatted_counts = {}

        for bitstring, count in counts.items():
            try:
                decimal_key = str(int(bitstring, 2))
                formatted_counts[decimal_key] = count
            except ValueError:
                logger.warning(f"Non-binary measurement result: {bitstring}")
                formatted_counts[bitstring] = count

        return formatted_counts

    def get_result_from_qasm(self, qasm_string):
        """
        Wrapper method to get the result object from a QASM string.
        """
        return self.execute_qasm(qasm_string)
