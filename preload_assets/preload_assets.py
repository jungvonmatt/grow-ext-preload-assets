# -*- coding: utf-8 -*-
import uuid
from operator import itemgetter

from grow import extensions
from grow.documents import document, static_document
from grow.extensions import hooks


class AssetBundle(object):
    def __init__(self, doc):
        self._doc = doc
        # Used to determine where to print the finished styles
        self._placeholder = '/* {} */'.format(uuid.uuid4())
        # Stores registered paths
        self._files = []

    def __repr__(self):
        return '<AssetBundle({})>'.format(self._placeholder)

    def addFile(self, obj, priority=1):
        file = (obj, priority)
        if file not in self._files:
            self._files.append(file)
        # Return empty string to not print None if used with {{ }}
        return ''

    def emit(self):
        return self._placeholder

    def inject(self, content):
        # Check wether the content has the placeholder
        if self._placeholder not in content:
            return content

        bundle = []
        for obj, priority in self._files:
            src = obj.get('src')
            type = 'image' if src.endswith('.png') or src.endswith('.jpg') else 'video'
            attributes = {'as': type, 'href': src}

            if (obj.get('srcset')):
                attributes['imagesrcset'] = obj.get('srcset')

            if (obj.get('sizes')):
                attributes['imagesizes'] = obj.get('sizes')

            if (obj.get('media')):
                attributes['media'] = obj.get('media')

            output = ['<link rel="preload"']
            for key, value in attributes.items():
                output.append('{0}="{1}"'.format(key,value))

            output.append('>')
            bundle.append(' '.join(output))

        bundle = ''.join(bundle)
        return content.replace(self._placeholder, bundle)


class PreloadAssetsPreRenderHook(hooks.PreRenderHook):
    """Handle the post-render hook."""

    def should_trigger(self, previous_result, doc, original_body, *_args,
                       **_kwargs):
        """Only run for documents with contents"""

        # Check that it's not a StaticDocument
        if isinstance(doc, static_document.StaticDocument):
            return False

        return True

    def trigger(self, previous_result, doc, raw_content, *_args, **_kwargs):
        # Create bundles and attach them to doc
        bundle = AssetBundle(doc)
        # Expose AssetBundle.addFile via custom method name
        setattr(bundle, 'addAsset', bundle.addFile)

        # And attach the bundle to doc for use, check that it is not reserved
        setattr(doc, 'preload', bundle)

        return previous_result if previous_result else raw_content


class PreloadAssetsPostRenderHook(hooks.PostRenderHook):
    """Handle the post-render hook."""

    def should_trigger(self, previous_result, doc, original_body, *_args,
                       **_kwargs):
        """Only needs to trigger if pre-render hook added a stylesheet
        and there is content to render"""
        # Do not run for empty documents
        content = previous_result if previous_result else original_body
        if content is None:
            return False

        # Check that it's not a StaticDocument
        if isinstance(doc, static_document.StaticDocument):
            return False

        return True

    def trigger(self, previous_result, doc, raw_content, *_args, **_kwargs):
        content = previous_result if previous_result else raw_content

        bundle = getattr(doc, 'preload')
        content = bundle.inject(content)

        return content


class PreloadAssetsExtension(extensions.BaseExtension):
    """Inline Text Assets Extension."""

    def __init__(self, pod, config):
        super(PreloadAssetsExtension, self).__init__(pod, config)

    @property
    def available_hooks(self):
        """Returns the available hook classes."""
        return [
            PreloadAssetsPreRenderHook,
            PreloadAssetsPostRenderHook,
        ]
