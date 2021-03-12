/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.mobigen.nifi.PythonModuleService;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.lang.reflect.Field;
import java.lang.reflect.InvocationTargetException;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

import org.apache.nifi.annotation.documentation.CapabilityDescription;
import org.apache.nifi.annotation.documentation.Tags;
import org.apache.nifi.annotation.lifecycle.OnDisabled;
import org.apache.nifi.annotation.lifecycle.OnEnabled;
import org.apache.nifi.components.PropertyDescriptor;
import org.apache.nifi.controller.AbstractControllerService;
import org.apache.nifi.controller.ConfigurationContext;
import org.apache.nifi.logging.ComponentLog;
import org.apache.nifi.processor.exception.ProcessException;
import org.apache.nifi.processor.util.StandardValidators;
import org.apache.nifi.reporting.InitializationException;

@Tags({ "PythonModuleService" })
@CapabilityDescription("ControllerService for Python Module Subproccessor.")
public class PythonModuleService extends AbstractControllerService implements PythonService {

	public static final PropertyDescriptor PYTHON_COMMAND = new PropertyDescriptor.Builder().name("PYTHON_COMMAND")
			.defaultValue("/usr/bin/python3").displayName("Python Interpreter")
			.description("Input Python Interpreter Path").required(true)
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR).build();

	public static final PropertyDescriptor EXECUTE_COMMAND = new PropertyDescriptor.Builder().name("EXECUTE_COMMAND")
			.defaultValue("").displayName("Python Module Path").description("Input Python Module Path").required(true)
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR).build();

	public static final PropertyDescriptor ARG_COMMAND = new PropertyDescriptor.Builder().name("ARG_COMMAND")
			.defaultValue("").displayName("Arguments").description("Input Execute Arguments").required(true)
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR).build();

	private static final List<PropertyDescriptor> properties;

	static {
		final List<PropertyDescriptor> props = new ArrayList<>();
		props.add(PYTHON_COMMAND);
		props.add(EXECUTE_COMMAND);
		props.add(ARG_COMMAND);
		properties = Collections.unmodifiableList(props);
	}

	@Override
	protected List<PropertyDescriptor> getSupportedPropertyDescriptors() {
		return properties;
	}

	private Boolean IsAlive = true;
	private Queue<String> std_ins = new LinkedList<>();
	private Queue<String> std_outs = new LinkedList<>();
	private Queue<String> std_errs = new LinkedList<>();
	private SingleThreadPython singleThreadPython;
	private Thread thrd;

	/**
	 * @param context the configuration context
	 * @throws InitializationException   if unable to create a database connection
	 * @throws IOException
	 * @throws InvocationTargetException
	 * @throws IllegalArgumentException
	 * @throws IllegalAccessException
	 */
	@OnEnabled
	public void onEnabled(final ConfigurationContext context) throws InitializationException, IOException,
			IllegalAccessException, IllegalArgumentException, InvocationTargetException {
		ComponentLog logger = getLogger();
		logger.info("=======================================================>onEnabled");
		
		Queue<String> std_ins = new LinkedList<>();
		Queue<String> std_outs = new LinkedList<>();
		Queue<String> std_errs = new LinkedList<>();		
		
		singleThreadPython = new SingleThreadPython(context);
		thrd = new Thread(singleThreadPython, "PythonThread");
		thrd.start();
	}

	@SuppressWarnings("removal")
	@OnDisabled
	public void shutdown() throws InterruptedException {
		ComponentLog logger = getLogger();
		singleThreadPython.StopProccessor();
		
		Queue<String> std_ins = new LinkedList<>();
		Queue<String> std_outs = new LinkedList<>();
		Queue<String> std_errs = new LinkedList<>();	
		
		logger.info("=======================================================>shutdown");

	}

	@Override
	public Boolean Is_Alive() throws ProcessException {
		return IsAlive;
	}

	@Override
	public Queue<String> Get_StdOut() throws ProcessException {
		// TODO Auto-generated method stub
		return std_outs;
	}

	@Override
	public Queue<String> Get_StdErr() throws ProcessException {
		// TODO Auto-generated method stub
		return std_errs;
	}

	@Override
	public void Put_StdIn(String _std_in) throws ProcessException {
		// TODO Auto-generated method stub
		std_ins.add(_std_in);
	}

	public class SingleThreadPython implements Runnable {
		private ProcessBuilder processBuilder;
		private Process process;

		private ReadStdOut readStdOut;
		private Thread read_thrd;

		private ErrStdOut errStdOut;
		private Thread err_thrd;

		private WriteStdIn writeStdIn;
		private Thread write_thrd;

		private boolean is_continue = true;

		public SingleThreadPython(ConfigurationContext context) throws IOException {
			ComponentLog logger = getLogger();
			String python_interpreter = context.getProperty(PYTHON_COMMAND).getValue();
			String python_module = context.getProperty(EXECUTE_COMMAND).getValue();
			String arguments = context.getProperty(ARG_COMMAND).getValue();
			String[] args = arguments.split("\\s+");
			String[] cmd = new String[args.length + 2];
			cmd[0] = python_interpreter;
			cmd[1] = python_module;
			int i = 2;
			for (String arg : args) {
				cmd[i] = arg;
				i++;
			}
			processBuilder = new ProcessBuilder(cmd);

		}

		public void StopProccessor() throws InterruptedException {

			this.is_continue = false;

			process.destroyForcibly();
			process.waitFor();
 
			readStdOut.Stop();
			errStdOut.Stop();
			writeStdIn.Stop();
		}

		@Override
		public void run() {
			ComponentLog logger = getLogger();

			try {
				IsAlive = true;
				process = processBuilder.start();

				readStdOut = new ReadStdOut(process);
				read_thrd = new Thread(readStdOut, "readStdOut");
				read_thrd.start();

				errStdOut = new ErrStdOut(process);
				err_thrd = new Thread(errStdOut, "errStdOut");
				err_thrd.start();

				writeStdIn = new WriteStdIn(process);
				write_thrd = new Thread(writeStdIn, "writeStdIn");
				write_thrd.start();

				while (this.is_continue) {
					if (Thread.interrupted()) {
						IsAlive = false;
						break;
					}
					if (!process.isAlive()) {
						IsAlive = false;
						break;
					}
					Thread.sleep(500);
				}

			} catch (IOException | InterruptedException e1) {
				// TODO Auto-generated catch block
				StringWriter sw = new StringWriter();
				e1.printStackTrace(new PrintWriter(sw));
				String exceptionAsString = sw.toString();
				logger.info("===========>" + exceptionAsString);
				this.is_continue = false;
			}

		}

		private int tryGetPid(Process process) {
			if (process.getClass().getName().equals("java.lang.UNIXProcess")) {
				try {
					Field f = process.getClass().getDeclaredField("pid");
					f.setAccessible(true);
					return f.getInt(process);
				} catch (IllegalAccessException | IllegalArgumentException | NoSuchFieldException
						| SecurityException e) {
				}
			}

			return -1;
		}
	}

	public class ReadStdOut implements Runnable {
		private Process process;
		private boolean is_continue = true;

		public ReadStdOut(Process _process) throws IOException {
			process = _process;
		}

		@Override
		public void run() {
			ComponentLog logger = getLogger();
			InputStream stdout = process.getInputStream();
			BufferedReader reader = new BufferedReader(new InputStreamReader(stdout));
			String line = "";
			try {
				while ((line = reader.readLine()) != null && is_continue) {
//					logger.info("READ=======================================================>" + line);
					std_outs.add(line);
				}
			} catch (IOException e) {
				// TODO Auto-generated catch block
				StringWriter sw = new StringWriter();
				e.printStackTrace(new PrintWriter(sw));
				String exceptionAsString = sw.toString();
				logger.info("===========>" + exceptionAsString);
				this.is_continue = false;
			}
		}

		public void Stop() {
			this.is_continue = false;
		}
	}

	public class ErrStdOut implements Runnable {
		private Process process;
		private boolean is_continue = true;

		public ErrStdOut(Process _process) throws IOException {
			process = _process;
		}

		@Override
		public void run() {
			ComponentLog logger = getLogger();
			InputStream stderr = process.getErrorStream();
			BufferedReader reader = new BufferedReader(new InputStreamReader(stderr));
			String line = "";
			try {
				while ((line = reader.readLine()) != null && is_continue) {
					std_errs.add(line);
				}
			} catch (IOException e) {
				// TODO Auto-generated catch block
				StringWriter sw = new StringWriter();
				e.printStackTrace(new PrintWriter(sw));
				String exceptionAsString = sw.toString();
				logger.info("===========>" + exceptionAsString);
				this.is_continue = false;
			}
		}

		public void Stop() {
			this.is_continue = false;
		}
	}

	public class WriteStdIn implements Runnable {
		private Process process;
		private boolean is_continue = true;

		public WriteStdIn(Process _process) throws IOException {
			process = _process;

		}

		@SuppressWarnings({ "static-access", "resource" })
		@Override
		public void run() {
			ComponentLog logger = getLogger();
			OutputStream stdin = process.getOutputStream();
			try {
				while (is_continue) {
					if (!std_ins.isEmpty()) {
						String msg = std_ins.poll();
						if (msg != null) {
							try {
								stdin.write(msg.getBytes(Charset.forName("UTF-8")));
								stdin.write('\n');
								stdin.flush();

							} catch (IOException e) {
								// TODO Auto-generated catch block
								StringWriter sw = new StringWriter();
								e.printStackTrace(new PrintWriter(sw));
								String exceptionAsString = sw.toString();
								logger.info("===========>" + exceptionAsString);
								this.is_continue = false;
							}
						}
					}
					Thread.sleep(100);
				}
			} catch (InterruptedException e) {
				// TODO Auto-generated catch block
				StringWriter sw = new StringWriter();
				e.printStackTrace(new PrintWriter(sw));
				String exceptionAsString = sw.toString();
				logger.info("===========>" + exceptionAsString);
				this.is_continue = false;
			}
		}

		public void Stop() {
			this.is_continue = false;
		}
	}

}
