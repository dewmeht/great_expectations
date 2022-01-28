import copy
from typing import Dict, List, Optional

from great_expectations.rule_based_profiler.domain_builder import (
    Domain,
    DomainBuilder,
)
from great_expectations.rule_based_profiler.parameter_builder import (
    ParameterBuilder,
    ParameterContainer,
)
from great_expectations.core import ExpectationConfiguration
from great_expectations.rule_based_profiler.expectation_configuration_builder import ExpectationConfigurationBuilder


class Rule:
    def __init__(
        self,
        rule_based_profiler: "RuleBasedProfiler",  # noqa: F821
        name: str,
        domain_builder: Optional[DomainBuilder] = None,
        parameter_builders: Optional[List[ParameterBuilder]] = None,
        expectation_configuration_builders: List[ExpectationConfigurationBuilder] = None,
    ):
        """
        Sets Profiler rule name, domain builders, parameters builders, configuration builders,
        and other necessary instance data (variables)
        :param rule_based_profiler: RuleBaseProfiler (parent) object
        :param name: A string representing the name of the ProfilerRule
        :param domain_builder: A Domain Builder object used to build rule data domain
        :param parameter_builders: A Parameter Builder list used to configure necessary rule evaluation parameters for
        every configuration
        :param expectation_configuration_builders: A list of Expectation Configuration Builders
        """
        self._rule_based_profiler = rule_based_profiler
        self._name = name
        self._domain_builder = domain_builder
        self._parameter_builders = parameter_builders
        self._expectation_configuration_builders = expectation_configuration_builders

        self._parameters = {}

    def generate(
        self,
        variables: Optional[ParameterContainer] = None,
    ) -> List[ExpectationConfiguration]:
        """
        Builds a list of Expectation Configurations, returning a single Expectation Configuration entry for every
        ConfigurationBuilder available based on the instantiation.

        :return: List of Corresponding Expectation Configurations representing every configured rule
        """
        if variables is None:
            variables = self.rule_based_profiler.variables

        expectation_configurations: List[ExpectationConfiguration] = []

        domains: List[Domain] = self._domain_builder.get_domains(variables=variables)

        domain: Domain
        for domain in domains:
            parameter_container: ParameterContainer = ParameterContainer(
                parameter_nodes=None
            )
            self._parameters[domain.id] = parameter_container
            parameter_builder: ParameterBuilder
            for parameter_builder in self._parameter_builders:
                parameter_builder.build_parameters(
                    parameter_container=parameter_container,
                    domain=domain,
                    variables=variables,
                    parameters=self.parameters,
                )

            expectation_configuration_builder: ExpectationConfigurationBuilder
            for (
                expectation_configuration_builder
            ) in self._expectation_configuration_builders:
                expectation_configurations.append(
                    expectation_configuration_builder.build_expectation_configuration(
                        domain=domain,
                        variables=variables,
                        parameters=self.parameters,
                    )
                )

        return expectation_configurations

    @property
    def rule_based_profiler(self) -> "RuleBasedProfiler":  # noqa: F821
        return self._rule_based_profiler

    @property
    def name(self) -> str:
        return self._name

    @property
    def domain_builder(self) -> DomainBuilder:
        return self._domain_builder

    @property
    def parameter_builders(self) -> Optional[Dict[str, ParameterBuilder]]:
        if self._parameter_builders is None:
            return None

        parameter_builder: ParameterBuilder
        return {parameter_builder.name: parameter_builder for parameter_builder in self._parameter_builders}

    @property
    def expectation_configuration_builders(self) -> Dict[str, ExpectationConfigurationBuilder]:
        expectation_configuration_builder: ExpectationConfigurationBuilder
        return {expectation_configuration_builder.expectation_type: expectation_configuration_builder for expectation_configuration_builder in self._expectation_configuration_builders}

    @property
    def parameters(self) -> Dict[str, ParameterContainer]:
        # Returning a copy of the "self._parameters" state variable in order to prevent write-before-read hazard.
        return copy.deepcopy(self._parameters)
