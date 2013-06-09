from hyde.ext.plugins.images import ImageThumbnailsPlugin

class FixedImageThumbnailsPlugin(ImageThumbnailsPlugin):
    """
    Provide a function to get thumbnail for any image resource.

    Example of usage:
    Setting optional defaults in site.yaml:
        thumbnails:
          width: 100
          height: 120
          prefix: thumbnail_

    Setting thumbnails options in nodemeta.yaml:
        thumbnails:
          - width: 50
            prefix: thumbs1_
            include:
            - '*.png'
            - '*.jpg'
          - height: 100
            prefix: thumbs2_
            include:
            - '*.png'
            - '*.jpg'
          - larger: 100
            prefix: thumbs3_
            include:
            - '*.jpg'
          - smaller: 50
            prefix: thumbs4_
            include:
            - '*.jpg'
    which means - make four thumbnails from every picture with different prefixes
    and sizes

    It is only valid to specify either width/height or larger/smaller, but not to
    mix the two types.

    If larger/smaller are specified, then the orientation (i.e., landscape or
    portrait) is preserved while thumbnailing.

    If both width and height (or both larger and smaller) are defined, the
    image is cropped. You can define crop_type as one of these values:
    "topleft", "center" and "bottomright".  "topleft" is default.
    """

    def __init__(self, site):
        super(FixedImageThumbnailsPlugin, self).__init__(site)

    def thumb(self, resource, width, height, prefix, crop_type, preserve_orientation=False):
        """
        Generate a thumbnail for the given image
        """
        name = os.path.basename(resource.get_relative_deploy_path())
        # don't make thumbnails for thumbnails
        if name.startswith(prefix):
            return
        # Prepare path, make all thumnails in single place(content/.thumbnails)
        # for simple maintenance but keep original deploy path to preserve
        # naming logic in generated site
        path = os.path.join(".thumbnails",
                            os.path.dirname(resource.get_relative_deploy_path()),
                            "%s%s" % (prefix, name))
        target = resource.site.config.content_root_path.child_file(path)
        res = self.site.content.add_resource(target)
        res.set_relative_deploy_path(res.get_relative_deploy_path().replace('.thumbnails/', '', 1))

        target.parent.make()
        if os.path.exists(target.path) and os.path.getmtime(resource.path) <= os.path.getmtime(target.path):
            return
        self.logger.debug("Making thumbnail for [%s]" % resource)

        im = self.Image.open(resource.path)
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        format = im.format

        if preserve_orientation and im.size[1] > im.size[0]:
          width, height = height, width

        resize_width, resize_height = thumb_scale_size(im.size[0], im.size[1], width, height)

        self.logger.debug("Resize to: %d,%d" % (resize_width, resize_height))
        im = im.resize((resize_width, resize_height), self.Image.ANTIALIAS)
        if width is not None and height is not None:
            shiftx = shifty = 0
            if crop_type == "center":
                shiftx = (im.size[0] - width)/2
                shifty = (im.size[1] - height)/2
            elif crop_type == "bottomright":
                shiftx = (im.size[0] - width)
                shifty = (im.size[1] - height)
            im = im.crop((shiftx, shifty, width + shiftx, height + shifty))
            im.load()

        options = dict(optimize=True)
        if format == "JPEG":
          options['quality'] = 75

        im.save(target.path, **options)

    def begin_site(self):
        """
        Find any image resource that should be thumbnailed and call thumb on it.
        """
        # Grab default values from config
        config = self.site.config
        defaults = { "width": None,
                     "height": None,
                     "larger": None,
                     "smaller": None,
                     "crop_type": "topleft",
                     "prefix": 'thumb_'}
        if hasattr(config, 'thumbnails'):
            defaults.update(config.thumbnails)

        for node in self.site.content.walk():
            if hasattr(node, 'meta') and hasattr(node.meta, 'thumbnails'):
                for th in node.meta.thumbnails:
                    if not hasattr(th, 'include'):
                        self.logger.error("Include is not set for node [%s]" % node)
                        continue
                    include = th.include
                    prefix = th.prefix if hasattr(th, 'prefix') else defaults['prefix']
                    height = th.height if hasattr(th, 'height') else defaults['height']
                    width = th.width if hasattr(th, 'width') else defaults['width']
                    larger = th.larger if hasattr(th, 'larger') else defaults['larger']
                    smaller = th.smaller if hasattr(th, 'smaller') else defaults['smaller']
                    crop_type = th.crop_type if hasattr(th, 'crop_type') else defaults['crop_type']
                    if crop_type not in ["topleft", "center", "bottomright"]:
                        self.logger.error("Unknown crop_type defined for node [%s]" % node)
                        continue
                    if width is None and height is None and larger is None and smaller is None:
                        self.logger.error("At least one of width, height, larger, or smaller must be set for node [%s]" % node)
                        continue

                    if ((larger is not None or smaller is not None) and
                        (width is not None or height is not None)):
                        self.logger.error("It is not valid to specify both one of width/height and one of larger/smaller for node [%s]" % node)
                        continue

                    if larger is None and smaller is None:
                      preserve_orientation = False
                      dim1, dim2 = width, height
                    else:
                      preserve_orientation = True
                      dim1, dim2 = larger, smaller

                    match_includes = lambda s: any([glob.fnmatch.fnmatch(s, inc) for inc in include])

                    for resource in node.resources:
                        if match_includes(resource.path):
                            self.thumb(resource, dim1, dim2, prefix, crop_type, preserve_orientation)

