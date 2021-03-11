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
package mobigen.processors.FileSplitter;

import org.apache.nifi.components.AllowableValue;
import org.apache.nifi.components.PropertyDescriptor;
import org.apache.nifi.flowfile.FlowFile;
import org.apache.nifi.logging.ComponentLog;
import org.apache.nifi.annotation.behavior.ReadsAttribute;
import org.apache.nifi.annotation.behavior.ReadsAttributes;
import org.apache.nifi.annotation.behavior.WritesAttribute;
import org.apache.nifi.annotation.behavior.WritesAttributes;
import org.apache.nifi.annotation.lifecycle.OnScheduled;
import org.apache.nifi.annotation.documentation.CapabilityDescription;
import org.apache.nifi.annotation.documentation.SeeAlso;
import org.apache.nifi.annotation.documentation.Tags;
import org.apache.nifi.processor.exception.ProcessException;
import org.apache.nifi.processor.io.InputStreamCallback;
import org.apache.nifi.processor.io.OutputStreamCallback;
import org.apache.nifi.processor.io.StreamCallback;
import org.apache.nifi.processor.AbstractProcessor;
import org.apache.nifi.processor.ProcessContext;
import org.apache.nifi.processor.ProcessSession;
import org.apache.nifi.processor.ProcessorInitializationContext;
import org.apache.nifi.processor.Relationship;
import org.apache.nifi.processor.util.StandardValidators;
import org.apache.nifi.util.StringUtils;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

@Tags({ "FileSplitter" })
@CapabilityDescription("Data File Labeling for Iris Load")
@SeeAlso({})
@ReadsAttributes({ @ReadsAttribute(attribute = "", description = "") })
@WritesAttributes({ @WritesAttribute(attribute = "", description = "") })
public class FileSplitter extends AbstractProcessor {

	public static final PropertyDescriptor MAX_FILE_SIZE = new PropertyDescriptor.Builder().name("MAX_FILE_SIZE")
			.displayName("Maximum File Size").description("Input Maximum file size of dividing files")
			.defaultValue("10000000").addValidator(StandardValidators.LONG_VALIDATOR).required(true).build();

	public static final PropertyDescriptor COL_IDX_PARTITION_DATE = new PropertyDescriptor.Builder()
			.name("COL_IDX_PARTITION_DATE").displayName("Partition Date Column Index")
			.description("Input Column Index of Partition date").defaultValue("0")
			.addValidator(StandardValidators.INTEGER_VALIDATOR).required(true).build();

	public static final PropertyDescriptor COL_IDX_PARTITION_KEY = new PropertyDescriptor.Builder()
			.name("COL_IDX_PARTITION_KEY").displayName("Partition Key Column Index")
			.description("Input Column Index of Partition key").defaultValue("1")
			.addValidator(StandardValidators.INTEGER_VALIDATOR).required(true).build();

	public static final PropertyDescriptor FIELD_SEP = new PropertyDescriptor.Builder().name("FIELD_SEP")
			.displayName("Field Seperator").description("Input Field seperator of data").defaultValue("|")
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR).required(true).build();

	public static final PropertyDescriptor FILE_EXT = new PropertyDescriptor.Builder().name("FILE_EXT")
			.displayName("File Extension").description("Input File Extension of output files").defaultValue("irs")
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR).required(true).build();

	public static final AllowableValue LNX_NEWLINE = new AllowableValue("\n", "\\n", "Linux Newline");
	public static final AllowableValue WND_NEWLINE = new AllowableValue("\r\n", "\\r\\n", "Windows Newline");

	public static final PropertyDescriptor RECORD_SEP = new PropertyDescriptor.Builder().name("RECORD_SEP")
			.displayName("Record Seperator").description("Record Separator").allowableValues(LNX_NEWLINE, WND_NEWLINE)
			.defaultValue("\n").build();

	public static final Relationship success = new Relationship.Builder().name("success")
			.description("Connect to IrisLoader or PutFile Processor for split files when success").build();

	public static final Relationship failure = new Relationship.Builder().name("failure").autoTerminateDefault(true)
			.description("Connect to PutFile Processor for split files when failure").build();

	private List<PropertyDescriptor> descriptors;

	private Set<Relationship> relationships;

	@Override
	protected void init(final ProcessorInitializationContext context) {
		final List<PropertyDescriptor> descriptors = new ArrayList<PropertyDescriptor>();
		descriptors.add(MAX_FILE_SIZE);
		descriptors.add(COL_IDX_PARTITION_DATE);
		descriptors.add(COL_IDX_PARTITION_KEY);
		descriptors.add(FIELD_SEP);
		descriptors.add(RECORD_SEP);
		descriptors.add(FILE_EXT);
		this.descriptors = Collections.unmodifiableList(descriptors);

		final Set<Relationship> relationships = new HashSet<Relationship>();
		relationships.add(success);
		relationships.add(failure);
		this.relationships = Collections.unmodifiableSet(relationships);
	}

	@Override
	public Set<Relationship> getRelationships() {
		return this.relationships;
	}

	@Override
	public final List<PropertyDescriptor> getSupportedPropertyDescriptors() {
		return descriptors;
	}

	@OnScheduled
	public void onScheduled(final ProcessContext context) {

	}

	@Override
	public void onTrigger(final ProcessContext context, final ProcessSession session) throws ProcessException {
		ComponentLog logger = getLogger();
		FlowFile flowFile = session.get();
		if (flowFile == null) {
			return;
		}

		final StringBuffer sb = new StringBuffer();

		session.read(flowFile, new InputStreamCallback() {
			@Override
			public void process(InputStream in) throws IOException {
//				fileLabeling(logger, context, session, in, flowFile);
				fileSplit(logger, context, session, in, flowFile);
			}
		});

		session.remove(flowFile);
	}

	public static Long tryParseLong(Object obj) {
		Long retVal;
		try {
			retVal = Long.parseLong((String) obj);
		} catch (NumberFormatException nfe) {
			retVal = (long) 0;
		}
		return retVal;
	}

	public static Integer tryParseInt(Object obj) {
		Integer retVal;
		try {
			retVal = Integer.parseInt((String) obj);
		} catch (NumberFormatException nfe) {
			retVal = (int) 0;
		}
		return retVal;
	}

	private static void fileSplit(ComponentLog logger, final ProcessContext context, final ProcessSession session,
			InputStream inputStream, FlowFile flowFile) {

		try {

			String org_filename = flowFile.getAttribute("filename");
			long max_file_size = (long) tryParseLong(context.getProperty(MAX_FILE_SIZE).getValue());
			int p_date_idx = (int) tryParseInt(context.getProperty(COL_IDX_PARTITION_DATE).getValue());
			int p_key_idx = (int) tryParseInt(context.getProperty(COL_IDX_PARTITION_KEY).getValue());
			String field_sep = context.getProperty(FIELD_SEP).getValue();
			String record_sep = context.getProperty(RECORD_SEP).getValue();
			String file_ext = context.getProperty(FILE_EXT).getValue();
			BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
			int i = 0;
			String line;
			long strBytes = 0;
			String curr_partition_date = "";
			String curr_partition_key = "";
			String curr_line = "";
			String fname = "";
			String curr_fname = "";

			Map<String, FlowFile> map_flowFiles = new HashMap<>();

			while ((line = reader.readLine()) != null) {
				String newLine = line + record_sep;
				String[] splt_line = line.split("[" + field_sep + "]");
				if (splt_line.length > p_date_idx && splt_line.length > p_key_idx) {
					curr_partition_date = splt_line[p_date_idx].toString().trim();
					curr_partition_key = splt_line[p_key_idx].toString().trim();
					if (!curr_fname.startsWith(String.format("flow_%s_%s", curr_partition_date, curr_partition_key))) {
						curr_fname = String.format("flow_%s_%s_%s", curr_partition_date, curr_partition_key, i);
					}
					if (map_flowFiles.containsKey(curr_fname) && (strBytes < max_file_size)) {
						session.append(map_flowFiles.get(curr_fname), new OutputStreamCallback() {
							@Override
							public void process(OutputStream out) throws IOException {
								out.write(newLine.getBytes());
							}
						});
						strBytes = strBytes + newLine.getBytes().length;
					} else {
						curr_fname = String.format("flow_%s_%s_%s", curr_partition_date, curr_partition_key, i);
						strBytes = 0;
						map_flowFiles.put(String.format("flow_%s_%s_%s", curr_partition_date, curr_partition_key, i),
								session.create());
						session.putAttribute(
								map_flowFiles.get(
										String.format("flow_%s_%s_%s", curr_partition_date, curr_partition_key, i)),
								"partition_date", curr_partition_date);
						session.putAttribute(
								map_flowFiles.get(
										String.format("flow_%s_%s_%s", curr_partition_date, curr_partition_key, i)),
								"partition_key", curr_partition_key);
						session.putAttribute(
								map_flowFiles.get(
										String.format("flow_%s_%s_%s", curr_partition_date, curr_partition_key, i)),
								"filename", String.format("%s_%s_%s_%s.irs", org_filename, i, curr_partition_date,
										curr_partition_key));
						session.append(
								map_flowFiles.get(
										String.format("flow_%s_%s_%s", curr_partition_date, curr_partition_key, i)),
								new OutputStreamCallback() {
									@Override
									public void process(OutputStream out) throws IOException {
										out.write(newLine.getBytes());
									}
								});
						i = i + 1;
						strBytes = strBytes + newLine.getBytes().length;
					}

				} else {
					if (map_flowFiles.containsKey("fail") && (strBytes < max_file_size)) {
						session.append(map_flowFiles.get("fail"), new OutputStreamCallback() {
							@Override
							public void process(OutputStream out) throws IOException {
								out.write(newLine.getBytes());
							}
						});

					} else {
						map_flowFiles.put("fail", session.create());
						session.putAttribute(map_flowFiles.get("fail"), "partition_date", curr_partition_date);
						session.putAttribute(map_flowFiles.get("fail"), "partition_key", curr_partition_key);
						session.putAttribute(map_flowFiles.get("fail"), "filename",
								String.format("%s_%s.irs", org_filename, "fail"));
						session.append(map_flowFiles.get("fail"), new OutputStreamCallback() {
							@Override
							public void process(OutputStream out) throws IOException {
								out.write(newLine.getBytes());
							}
						});
					}

				}
			}

			if (map_flowFiles.containsKey("fail")) {
				session.transfer(map_flowFiles.get("fail"), failure);
			}
			map_flowFiles.remove("fail");
			session.transfer(map_flowFiles.values(), success);

		} catch (Exception e) {
			e.printStackTrace();
			StringWriter sw = new StringWriter();
			e.printStackTrace(new PrintWriter(sw));
			String exceptionAsString = sw.toString();
			logger.info(
					"FileSplit Exception=============================================================================================>");
			logger.info(exceptionAsString);
			logger.info(
					"<=============================================================================================FileSplit Exception");
		}

	}

	private static void fileLabeling(ComponentLog logger, final ProcessContext context, final ProcessSession session,
			InputStream inputStream, FlowFile flowFile) {

		try {
			String org_filename = flowFile.getAttribute("filename");
			long max_file_size = (long) tryParseLong(context.getProperty(MAX_FILE_SIZE).getValue());
			int p_date_idx = (int) tryParseInt(context.getProperty(COL_IDX_PARTITION_DATE).getValue());
			int p_key_idx = (int) tryParseInt(context.getProperty(COL_IDX_PARTITION_KEY).getValue());
			String field_sep = context.getProperty(FIELD_SEP).getValue();
			String record_sep = context.getProperty(RECORD_SEP).getValue();
			String file_ext = context.getProperty(FILE_EXT).getValue();
			BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
			int i = 0;
			String line;
			long strBytes = 0;
			String curr_partition_date = "";
			String curr_partition_key = "";
			String curr_line = "";

			ArrayList<FlowFile> FlowFiles = new ArrayList<FlowFile>();
			while (true) {
				boolean change_partition = false;
				strBytes = 0;
				line = "";

				FlowFile new_flowFile = session.create();
				FlowFiles.add(new_flowFile);
				try (OutputStream flowFileOutputStream = session.write(new_flowFile)) {
					if (curr_line.toString() != "") {
						flowFileOutputStream.write(curr_line.getBytes());
						String[] splt_line = curr_line.split("[" + field_sep + "]");

						if (splt_line.length > p_date_idx && splt_line.length > p_key_idx) {
							curr_partition_date = splt_line[p_date_idx].toString().trim();
							curr_partition_key = splt_line[p_key_idx].toString().trim();
						}

						curr_line = "";
					} else {

					}
					while ((line = reader.readLine()) != null) {
						String newLine = line + record_sep;
						String[] splt_line = line.split("[" + field_sep + "]");
						if (splt_line.length > p_date_idx && splt_line.length > p_key_idx) {
							if (curr_partition_date.compareTo(splt_line[p_date_idx].toString().trim()) != 0
									&& curr_partition_date.compareTo("") != 0) {
								change_partition = true;
							}
							if (curr_partition_key.compareTo(splt_line[p_key_idx].toString().trim()) != 0
									&& curr_partition_key.compareTo("") != 0) {
								change_partition = true;
							}

							if (!change_partition) {
								curr_partition_date = splt_line[p_date_idx].toString().trim();
								curr_partition_key = splt_line[p_key_idx].toString().trim();
								strBytes = strBytes + newLine.getBytes().length;
								flowFileOutputStream.write(newLine.getBytes());
							} else {
								curr_line = newLine;
							}
							if ((strBytes >= max_file_size) || change_partition) {
								break;
							}
						}
					}
				} catch (Exception e) {
					e.printStackTrace();
					StringWriter sw = new StringWriter();
					e.printStackTrace(new PrintWriter(sw));
					String exceptionAsString = sw.toString();
					logger.info(
							"=============================================================================================>");
					logger.info(exceptionAsString);
					logger.info(
							"<=============================================================================================");
				} finally {
					if (line == null || line.toString() == "") {
						session.putAttribute(new_flowFile, "partition_date", curr_partition_date);
						session.putAttribute(new_flowFile, "partition_key", curr_partition_key);
						session.putAttribute(new_flowFile, "filename", String.format("%s_%s_%s_%s.irs", org_filename, i,
								curr_partition_date, curr_partition_key));
//						session.transfer(new_flowFile, success);
//						
						break;
					} else {
						session.putAttribute(new_flowFile, "partition_date", curr_partition_date);
						session.putAttribute(new_flowFile, "partition_key", curr_partition_key);
						session.putAttribute(new_flowFile, "filename", String.format("%s_%s_%s_%s.irs", org_filename, i,
								curr_partition_date, curr_partition_key));
//						session.transfer(new_flowFile, success);
						i = i + 1;
					}
				}
			}

			session.transfer(FlowFiles, success);

		} catch (Exception e) {
			e.printStackTrace();
			StringWriter sw = new StringWriter();
			e.printStackTrace(new PrintWriter(sw));
			String exceptionAsString = sw.toString();
			logger.info(
					"=============================================================================================>");
			logger.info(exceptionAsString);
			logger.info(
					"<=============================================================================================");
		}
	}

}
