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
package com.mobigen.nifi.PythonModuleProcessor;

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
import org.apache.nifi.processor.AbstractProcessor;
import org.apache.nifi.processor.ProcessContext;
import org.apache.nifi.processor.ProcessSession;
import org.apache.nifi.processor.ProcessorInitializationContext;
import org.apache.nifi.processor.Relationship;
import org.apache.nifi.processor.util.StandardValidators;

import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Queue;
import java.util.Set;

import mobigen.PythonModuleService.*;
import mobigen.PythonModuleService.PythonModuleService.ReadStdOut;

@Tags({ "PythonModule" })
@CapabilityDescription("Provide a description")
@SeeAlso({})
@ReadsAttributes({ @ReadsAttribute(attribute = "", description = "") })
@WritesAttributes({ @WritesAttribute(attribute = "", description = "") })
public class PythonModuleProcessor extends AbstractProcessor {

	public static final PropertyDescriptor PYTHON_SERVICE = new PropertyDescriptor.Builder().name("PYTHON_SERVICE")
			.displayName("Python Controller Service").description("Select a Python Controller Service").required(true)
			.identifiesControllerService(PythonService.class).build();

	public static final PropertyDescriptor STDIN_PROPERTY = new PropertyDescriptor.Builder().name("STDIN_PROPERTY")
			.displayName("Std In Attribute").description("Input Standard In attribute from FlowFile")
			.defaultValue("${filename}").expressionLanguageSupported(true).required(true)
			.addValidator(StandardValidators.NON_EMPTY_VALIDATOR).build();

	public static final Relationship STD_OUT = new Relationship.Builder().name("STD_OUT")
			.description("Standard out from python module").build();

	private List<PropertyDescriptor> descriptors;

	private Set<Relationship> relationships;

	@Override
	protected void init(final ProcessorInitializationContext context) {
		final List<PropertyDescriptor> descriptors = new ArrayList<PropertyDescriptor>();
		descriptors.add(STDIN_PROPERTY);
		descriptors.add(PYTHON_SERVICE);
		this.descriptors = Collections.unmodifiableList(descriptors);

		final Set<Relationship> relationships = new HashSet<Relationship>();
		relationships.add(STD_OUT);
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
		ComponentLog logger = getLogger();
		logger.info("=======================================================>onScheduled");
	}

	@Override
	public void onTrigger(final ProcessContext context, final ProcessSession session) throws ProcessException {

		ComponentLog logger = getLogger();
		PythonService service = context.getProperty(PYTHON_SERVICE).asControllerService(PythonService.class);

		FlowFile flowFile = session.get();
		if (!service.Is_Alive()) {
			session.rollback();
			return;
		}
		if (flowFile != null) {
			String std_in_property = context.getProperty(STDIN_PROPERTY).evaluateAttributeExpressions(flowFile)
					.getValue();

//			logger.info("===========> in : " + std_in_property);
			service.Put_StdIn(std_in_property);
			try {
				Boolean is_check_stderr = false;
				while (!is_check_stderr) {
					Queue<String> errs = service.Get_StdErr();
					is_check_stderr = false;
					if (!errs.isEmpty()) {
//						logger.info("===========> !errs.isEmpty()");
						String err = errs.poll();
						err = err.replaceAll("\n", "");
						err = err.replaceAll("\r\n", "");
						
						String in = std_in_property.toString();
						in = in.replaceAll("\n", "");
						in = in.replaceAll("\r\n", "");
						
//						logger.info("===========> err : " + err);
						if (err.compareTo(in) == 0) {
//							logger.info("===========> is_check_stderr true");
							is_check_stderr = true;
						}
					}
				}

				Queue<String> outs = service.Get_StdOut();
				while (!outs.isEmpty()) {
					outs = service.Get_StdOut();
					String out = outs.poll();
					logger.info("===========> out : " + out);

					FlowFile new_flowfile = session.create();
					session.putAllAttributes(new_flowfile, flowFile.getAttributes());
					session.putAttribute(new_flowfile, "STD_OUT", out);
					session.transfer(new_flowfile, STD_OUT);
				}

				if (is_check_stderr) {
					session.remove(flowFile);
				} else {
					session.rollback();
				}

			} catch (Exception e) {
				StringWriter sw = new StringWriter();
				e.printStackTrace(new PrintWriter(sw));
				String exceptionAsString = sw.toString();
				logger.info("===========>" + exceptionAsString);
			}
		} else {
			Queue<String> outs = service.Get_StdOut();
			while (!outs.isEmpty()) {
				String out = outs.poll();
				FlowFile new_flowfile = session.create();
				session.putAttribute(new_flowfile, "STD_OUT", out);
				session.transfer(new_flowfile, STD_OUT);
			}
		}
	}

}
