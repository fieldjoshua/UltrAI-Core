"""
Output Formatter for Ultra Synthesis™

This module provides clean, well-structured output formatting for the
orchestration pipeline results.
"""

from typing import Dict, List, Any, Optional, Literal
import re
from datetime import datetime
import base64

from app.config.orchestrator_config import CONFIG  # type: ignore

Format = Literal["md", "text"]


class OutputFormatter:
    """
    Formats orchestration pipeline output for better readability and structure.
    """

    def __init__(self):
        """Initialize the output formatter."""
        self.section_separator = "\n" + "=" * 80 + "\n"
        self.subsection_separator = "\n" + "-" * 60 + "\n"

    def format_pipeline_output(
        self,
        pipeline_results: Dict[str, Any],
        include_initial_responses: bool = True,
        include_peer_review: bool = True,
        include_metadata: bool = False,
    ) -> Dict[str, Any]:
        """
        Format the complete pipeline output with proper structure.

        Args:
            pipeline_results: Raw pipeline results
            include_initial_responses: Whether to include initial model responses
            include_peer_review: Whether to include peer review responses
            include_metadata: Whether to include processing metadata

        Returns:
            Formatted output dictionary
        """
        formatted = {}

        # Extract stages
        initial_response = pipeline_results.get("initial_response", {})
        peer_review = pipeline_results.get("peer_review_and_revision", {})
        ultra_synthesis = pipeline_results.get("ultra_synthesis", {})

        # Format Ultra Synthesis as the main result
        if isinstance(ultra_synthesis, dict) and "synthesis" in ultra_synthesis:
            formatted["synthesis"] = self._format_synthesis(
                ultra_synthesis["synthesis"]
            )
            formatted["synthesis_model"] = ultra_synthesis.get("model_used", "Unknown")

        # Add initial responses if requested
        if include_initial_responses and initial_response:
            formatted["initial_responses"] = self._format_initial_responses(
                initial_response
            )

        # Add peer review responses if requested
        if include_peer_review and peer_review:
            formatted["peer_review_responses"] = self._format_peer_review(peer_review)

        # Add pipeline summary
        formatted["pipeline_summary"] = self._create_pipeline_summary(
            pipeline_results, include_metadata
        )

        # Add formatted full document
        formatted["full_document"] = self._create_full_document(
            formatted, pipeline_results
        )

        return formatted

    def _format_synthesis(self, synthesis_text: str) -> Dict[str, Any]:
        """Format the Ultra Synthesis text."""
        # Clean up the synthesis text
        cleaned_text = synthesis_text.strip()

        # Extract sections if they exist
        sections = self._extract_sections(cleaned_text)

        return {
            "text": cleaned_text,
            "sections": sections,
            "word_count": len(cleaned_text.split()),
            "formatted_text": self._add_formatting(cleaned_text),
        }

    def _format_initial_responses(
        self, initial_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format initial model responses."""
        responses = {}

        if "responses" in initial_response:
            for model, response in initial_response["responses"].items():
                responses[model] = {
                    "text": response,
                    "word_count": len(str(response).split()),
                    "preview": self._get_preview(response, 150),
                }

        return {
            "responses": responses,
            "model_count": len(responses),
            "successful_models": list(responses.keys()),
        }

    def _format_peer_review(self, peer_review: Dict[str, Any]) -> Dict[str, Any]:
        """Format peer review responses."""
        responses = {}

        if "revised_responses" in peer_review:
            for model, response in peer_review["revised_responses"].items():
                responses[model] = {
                    "text": response,
                    "word_count": len(str(response).split()),
                    "preview": self._get_preview(response, 150),
                }

        return {
            "responses": responses,
            "revision_count": peer_review.get("revision_count", 0),
            "models_with_revisions": list(responses.keys()),
        }

    def _create_pipeline_summary(
        self, pipeline_results: Dict[str, Any], include_metadata: bool
    ) -> Dict[str, Any]:
        """Create a summary of the pipeline execution."""
        summary = {"stages_completed": [], "total_models_used": set(), "success": True}

        # Track completed stages
        for stage in [
            "initial_response",
            "peer_review_and_revision",
            "ultra_synthesis",
        ]:
            if stage in pipeline_results:
                summary["stages_completed"].append(stage)

                # Extract models used
                stage_data = pipeline_results[stage]
                if isinstance(stage_data, dict):
                    if "successful_models" in stage_data:
                        summary["total_models_used"].update(
                            stage_data["successful_models"]
                        )
                    elif "model_used" in stage_data:
                        summary["total_models_used"].add(stage_data["model_used"])

        summary["total_models_used"] = list(summary["total_models_used"])
        summary["stage_count"] = len(summary["stages_completed"])

        if include_metadata:
            summary["metadata"] = {
                "timestamp": datetime.now().isoformat(),
                "pipeline_version": "3-stage optimized",
            }

        return summary

    def _create_full_document(
        self, formatted_data: Dict[str, Any], pipeline_results: Dict[str, Any]
    ) -> str:
        """Create a nicely formatted full document."""
        doc_parts = []

        # Header
        doc_parts.append("🌟 ULTRA SYNTHESIS™ RESULTS 🌟")
        doc_parts.append(self.section_separator)

        # Ultra Synthesis Section
        if "synthesis" in formatted_data:
            doc_parts.append("📊 ULTRA SYNTHESIS")
            doc_parts.append(self.subsection_separator)
            doc_parts.append(formatted_data["synthesis"]["formatted_text"])
            doc_parts.append(
                f"\n\n💡 Synthesized by: {formatted_data.get('synthesis_model', 'Unknown')}"
            )
            doc_parts.append(self.section_separator)

        # Initial Responses Section
        if "initial_responses" in formatted_data:
            initial = formatted_data["initial_responses"]
            doc_parts.append(f"🎯 INITIAL RESPONSES ({initial['model_count']} models)")
            doc_parts.append(self.subsection_separator)

            for model, response_data in initial["responses"].items():
                doc_parts.append(f"### {model}")
                doc_parts.append(response_data["preview"])
                doc_parts.append("")

        # Pipeline Summary
        if "pipeline_summary" in formatted_data:
            summary = formatted_data["pipeline_summary"]
            doc_parts.append(self.section_separator)
            doc_parts.append("📈 PIPELINE SUMMARY")
            doc_parts.append(self.subsection_separator)
            doc_parts.append(
                f"✅ Stages Completed: {', '.join(summary['stages_completed'])}"
            )
            doc_parts.append(
                f"🤖 Models Used: {', '.join(summary['total_models_used'])}"
            )
            doc_parts.append(f"📊 Total Stages: {summary['stage_count']}")

        return "\n".join(doc_parts)

    def _extract_sections(self, text: str) -> List[Dict[str, str]]:
        """Extract sections from the synthesis text."""
        sections = []

        # Look for markdown headers
        header_pattern = r"^(#{1,6})\s+(.+)$"

        lines = text.split("\n")
        current_section = None
        current_content = []

        for line in lines:
            header_match = re.match(header_pattern, line, re.MULTILINE)
            if header_match:
                # Save previous section
                if current_section:
                    sections.append(
                        {
                            "title": current_section,
                            "content": "\n".join(current_content).strip(),
                            "level": current_level,
                        }
                    )

                # Start new section
                current_level = len(header_match.group(1))
                current_section = header_match.group(2)
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_section:
            sections.append(
                {
                    "title": current_section,
                    "content": "\n".join(current_content).strip(),
                    "level": current_level,
                }
            )

        return sections

    def _add_formatting(self, text: str) -> str:
        """Add nice formatting to the synthesis text."""
        # Add emphasis to key phrases
        formatted = text

        # Bold important phrases
        important_phrases = [
            r"\b(key finding|important|significant|notable|critical)\b",
            r"\b(conclusion|summary|in conclusion|overall)\b",
            r"\b(recommendation|suggest|advise)\b",
        ]

        for phrase in important_phrases:
            formatted = re.sub(f"({phrase})", r"**\1**", formatted, flags=re.IGNORECASE)

        # Add bullet points for lists
        formatted = re.sub(r"^(\d+\.|\-|\*)\s+", r"• ", formatted, flags=re.MULTILINE)

        return formatted

    def _get_preview(self, text: str, max_length: int = 150) -> str:
        """Get a preview of the text."""
        if len(text) <= max_length:
            return text

        # Find a good break point
        preview = text[:max_length]
        last_space = preview.rfind(" ")
        if last_space > max_length * 0.8:  # If there's a space in the last 20%
            preview = preview[:last_space]

        return preview + "..."


def _encrypt(text: str, key: str) -> str:
    """Very simple reversible encoding (base64 XOR) placeholder.

    NOTE: For production-grade encryption, integrate libsodium / AES-GCM.
    This function provides minimal obfuscation only.
    """
    xor_bytes = bytes(a ^ b for a, b in zip(text.encode(), key.encode() * 1024))
    return base64.b64encode(xor_bytes).decode()


def _decrypt(encoded: str, key: str) -> str:
    data = base64.b64decode(encoded)
    xor_bytes = bytes(a ^ b for a, b in zip(data, key.encode() * 1024))
    return xor_bytes.decode()


def format_output(
    response: str,
    format: Format = "md",
    encrypt: bool = False,
    key: str | None = None,
    no_model_access: bool = False,
) -> str:
    """Post-process the Ultra response.

    Args:
        response: synthesized answer (markdown by default)
        format: "md" or "text"
        encrypt: If True, encrypt result using key or CONFIG.ENCRYPTION_KEY
        key: override key for encryption
        no_model_access: If True, redact content for LLM logs (returns placeholder)
    Returns:
        Final string ready for client delivery.
    """
    if no_model_access:
        response_to_return = "[REDACTED – no_model_access enabled]"
    else:
        response_to_return = response

    # Convert to plain text if requested
    if format == "text":
        # naive markdown strip
        response_to_return = re.sub(r"[\*_`#>-]", "", response_to_return)

    # Encrypt if requested
    if encrypt:
        used_key = key or CONFIG.ENCRYPTION_KEY
        if not used_key:
            raise ValueError("Encryption requested but no key provided or configured")
        response_to_return = _encrypt(response_to_return, used_key)

    return response_to_return


__all__ = ["format_output", "_decrypt"]
