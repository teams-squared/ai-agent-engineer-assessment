import logging
import json
from flask import Blueprint, request, Response, stream_with_context, jsonify
from pydantic import ValidationError

from ..models.pydantic_models import QueryRequest, ErrorResponse, PolicyResponse
from ..services.llm_service import llm_service_instance

logger = logging.getLogger(__name__)
api_blueprint = Blueprint('api', __name__, url_prefix='/api')

@api_blueprint.route('/health', methods=['GET'])
def health_check():
    """
    A simple health check endpoint to confirm the API is running.

    Returns:
        Response: A JSON response indicating the status of the API.
    """
    logger.info("Health check endpoint hit.")
    return jsonify({"status": "ok", "message": "Policy Assistant API is healthy."}), 200

@api_blueprint.route('/query', methods=['POST'])
def query_policy():
    """
    Handles user queries about policies.
    Accepts a JSON payload with 'question' and optional 'chat_history'.
    Streams a structured JSON response.

    Returns:
        Response: A streaming response with JSON data or an error message.
    """
    logger.info(f"Received POST request on /api/query. Headers: {request.headers}, Body: {request.data[:200]}...")

    if not request.is_json:
        logger.warning("Request content type is not application/json.")
        error_resp = ErrorResponse(error="Invalid request", details="Content-Type must be application/json.")
        return jsonify(error_resp.dict()), 415

    try:
        json_data = request.get_json()
        logger.debug(f"Parsed JSON data: {json_data}")
        query_data = QueryRequest(**json_data)
    except ValidationError as e:
        logger.error(f"Request validation error: {e.errors()}", exc_info=True)
        error_resp = ErrorResponse(error="Validation Error", details=e.errors())
        return jsonify(error_resp.dict()), 400
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}", exc_info=True)
        error_resp = ErrorResponse(error="Invalid JSON format", details=str(e))
        return jsonify(error_resp.dict()), 400
    except Exception as e:
        logger.error(f"Unexpected error parsing request: {str(e)}", exc_info=True)
        error_resp = ErrorResponse(error="Error processing request", details=str(e))
        return jsonify(error_resp.dict()), 400

    if not llm_service_instance:
        logger.critical("LLMService is not initialized. Cannot process query.")
        error_resp = ErrorResponse(error="Service Unavailable", details="The LLM service is currently not available.")
        return jsonify(error_resp.dict()), 503

    def generate_stream():
        """
        A generator function that streams the LLM response.
        Each event contains a JSON string of the PolicyResponse chunk.

        Yields:
            str: Server-Sent Events (SSE) formatted strings containing JSON data.
        """
        try:
            logger.info(f"Starting stream generation for question: '{query_data.question}', filter: {query_data.filter_on_metadata}")
            for response_chunk in llm_service_instance.stream_query_response(
                query_data.question,
                query_data.chat_history,
                query_data.filter_on_metadata
            ):
                if isinstance(response_chunk, PolicyResponse):
                    sse_event = f"data: {response_chunk.json()}\n\n"
                    logger.debug(f"Yielding SSE event: {sse_event.strip()}")
                    yield sse_event
                else:
                    logger.warning(f"Stream yielded unexpected data type: {type(response_chunk)}")
            logger.info(f"Finished stream generation for question: '{query_data.question}'")
        except Exception as e:
            logger.error(f"Error during stream generation: {e}", exc_info=True)
            error_obj = PolicyResponse(summary="Stream generation error", bullets=[str(e)])
            error_event = f"data: {error_obj.json()}\n\n"
            logger.debug(f"Yielding error SSE event: {error_event.strip()}")
            yield error_event

    return Response(stream_with_context(generate_stream()), mimetype='text/event-stream')

